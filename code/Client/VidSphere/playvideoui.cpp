//playvideoui.cpp

#include "playvideoui.h"
#include "./ui_playvideoui.h"
#include "video.h"
#include "downloadvideowidget.h"
#include "playvideo.h"
#include <QTimer>
#include <QPropertyAnimation>
#include <QGraphicsOpacityEffect>
#include <QMessageBox>
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonArray>
#include <QUrl>
#include <QListWidgetItem>
#include <QProgressBar>
#include <QSlider>
#include <QPushButton>
#include <QLabel>
#include <QLineEdit>
#include <QListWidget>
#include <QGroupBox>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QScrollArea>
#include <QGridLayout>
#include <QStackedWidget>
#include <QToolButton>
#include <QFileDialog>
#include <QFile>
#include <QMimeDatabase>
#include <QHttpMultiPart>
#include <QDesktopServices>
#include <QFileInfo>

// 初始化视频流客户端主界面
// 创建QNetworkAccessManager实例用于网络请求
PlayVideoUI::PlayVideoUI(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::PlayVideoUI)
    , networkManager(new QNetworkAccessManager(this))
    , playVideoController(new PlayVideo(this))
    , currentUploadFilePath("")
{
    ui->setupUi(this);
    // 设置客户端窗口
    setWindowTitle("客户端");
    resize(1000, 700);

    //初始化媒体播放器
    playVideoController->setVideoWidget(ui->videoWidget);
    //设置UI控制器
    playVideoController->setUIController(this);

    //禁用控制按钮（等待连接）
    ui->playButton->setEnabled(false);
    ui->pauseButton->setEnabled(false);
    ui->stopButton->setEnabled(false);

    // 连接按钮信号
    connect(ui->connectButton, &QPushButton::clicked, this, &PlayVideoUI::onConnectButtonClicked);

    //网络请求信号：只处理视频列表请求
    connect(networkManager, &QNetworkAccessManager::finished, this, &PlayVideoUI::onVideoListReceivedFromNetwork);

    // 初始化播放控制按钮的连接
    connect(ui->playButton, &QPushButton::clicked, this, &PlayVideoUI::onPlayButtonClicked);
    connect(ui->pauseButton, &QPushButton::clicked, this, &PlayVideoUI::onPauseButtonClicked);
    connect(ui->stopButton, &QPushButton::clicked, this, &PlayVideoUI::onStopButtonClicked);
    connect(ui->volumeSlider, &QSlider::valueChanged, this, &PlayVideoUI::onVolumeSliderChanged);

    // 连接返回按钮
    connect(ui->returnButton, &QToolButton::clicked, this, &PlayVideoUI::onReturnButtonClicked);

    // 连接下载按钮到下载请求信号
    connect(ui->downloadButton, &QPushButton::clicked, this, &PlayVideoUI::onDownloadButtonClicked);

    // 连接上传按钮
    connect(ui->browseButton, &QPushButton::clicked, this, &PlayVideoUI::onBrowseButtonClicked);
    connect(ui->uploadButton, &QPushButton::clicked, this, &PlayVideoUI::onUploadButtonClicked);
    
    // 连接刷新按钮
    connect(ui->refreshButton, &QPushButton::clicked, this, &PlayVideoUI::onRefreshButtonClicked);
}

PlayVideoUI::~PlayVideoUI()
{
    delete ui;
}

// 处理连接服务器按钮点击事件
void PlayVideoUI::onConnectClicked()
{
    //获取服务器地址输入
    serverAddress = ui->serverInput->text().trimmed();

    if (serverAddress.isEmpty()) {
        QMessageBox::warning(this, "警告", "请输入服务器地址");
        return;
    }

    //更新状态标签
    ui->statusLabel->setText("正在连接到服务器...");
    clearVideoList();
    videoList.clear();
    videoDetails.clear();

    // 获取视频列表
    loadVideoList();
}

// 显示视频列表界面
void PlayVideoUI::showVideoList()
{
    ui->mainStackedWidget->setCurrentIndex(0);
    //QStackedWidget.setCurrentIndex()切换到视频列表页面
    
    // 禁用播放控制按钮
    ui->playButton->setEnabled(false);
    ui->pauseButton->setEnabled(false);
    ui->stopButton->setEnabled(false);
}

// 显示视频播放界面
void PlayVideoUI::showVideoPlayer()
{
    ui->mainStackedWidget->setCurrentIndex(1); // 显示视频播放界面
    
    // 确保播放控制按钮已启用
    ui->playButton->setEnabled(true);
    ui->pauseButton->setEnabled(true);
    ui->stopButton->setEnabled(true);
}

// 清空视频列表显示——————
void PlayVideoUI::clearVideoList()
{
    // 删除所有视频小部件
    QLayoutItem *child;
    QGridLayout *layout = ui->videoListLayout;
    //QGridLayout.takeAt()移除布局项
    while ((child = layout->takeAt(0)) != nullptr) {
        delete child->widget();
        delete child;
    }
}

// 处理返回视频列表事件
void PlayVideoUI::onReturnToListClicked()
{
    playVideoController->stop(); //停止当前播放
    showVideoList();
    ui->statusLabel->setText("已返回视频列表");
}

// 处理选择上传视频文件事件
void PlayVideoUI::onUploadVideoSelected()
{
    QString fileName = QFileDialog::getOpenFileName(this,
                                                    "选择视频文件",
                                                    "",
                                                    "视频文件 (*.mp4 *.avi *.mov *.mkv *.wmv *.flv *.webm)");

    if (!fileName.isEmpty()) {
        ui->selectedVideoPath->setText(fileName);
        currentUploadFilePath = fileName;
        ui->uploadButton->setEnabled(true);
        ui->statusLabel->setText("已选择视频文件: " + QFileInfo(fileName).fileName());
    }
}

// 处理上传视频按钮点击事件
void PlayVideoUI::onUploadClicked()
{
    if (currentUploadFilePath.isEmpty()) {
        QMessageBox::warning(this, "警告", "请先选择视频文件");
        return;
    }
    if (serverAddress.isEmpty()) {
        QMessageBox::warning(this, "警告", "请先连接到服务器");
        return;
    }

    // 准备上传请求——————QHttpMultiPart.prepare()准备multipart请求
    QHttpMultiPart *multiPart = new QHttpMultiPart(QHttpMultiPart::FormDataType, this);

    // 添加视频文件——————
    QHttpPart videoPart;
    videoPart.setHeader(QNetworkRequest::ContentDispositionHeader,
                        QVariant("form-data; name=\"video\"; filename=\"" + QFileInfo(currentUploadFilePath).fileName()
                                 + "\""));

    QFile *file = new QFile(currentUploadFilePath);
    if (!file->open(QIODevice::ReadOnly)) {
        QMessageBox::critical(this, "错误", "无法打开视频文件: " + file->errorString());
        delete file;
        delete multiPart;
        return;
    }

    videoPart.setBodyDevice(file);
    file->setParent(multiPart); // 让 QHttpMultiPart 管理文件的生命周期

    multiPart->append(videoPart);

    // 构建上传URL
    QUrl uploadUrl(serverAddress + "/upload");
    QNetworkRequest request(uploadUrl);

    // 发送POST请求
    QNetworkReply *reply = networkManager->post(request, multiPart);
    multiPart->setParent(reply); // 让 QNetworkReply 管理 QHttpMultiPart 的生命周期

    // 连接上传完成信号
    connect(reply, &QNetworkReply::finished, this, [this, reply]() {
        // 检查是否是上传请求的回复
        if (reply->url().toString().contains("/upload")) { onVideoUploaded(reply); }
        reply->deleteLater();
    });

    ui->statusLabel->setText("正在上传视频...");
}

// 处理视频上传完成响应
void PlayVideoUI::onVideoUploaded(QNetworkReply *reply)
{
    if (reply->error() != QNetworkReply::NoError) {
        ui->statusLabel->setText("上传失败: " + reply->errorString());
        QMessageBox::critical(this, "错误", "视频上传失败:\n" + reply->errorString());
        return;
    }

    // 读取响应数据，QNetworkReply.readAll()读取响应数据
    QByteArray responseData = reply->readAll();

    // 解析响应，QJsonDocument.fromJson()解析JSON响应
    QJsonDocument jsonDoc = QJsonDocument::fromJson(responseData);
    if (!jsonDoc.isObject()) {
        ui->statusLabel->setText("上传响应格式错误");
        return;
    }

    // QJsonObject.operator[]()获取响应字段
    QJsonObject jsonObj = jsonDoc.object();
    if (jsonObj["success"].toBool()) {
        QString filename = jsonObj["filename"].toString();

        // 显示上传成功消息
        ui->statusLabel->setText("视频上传成功！");

        // 清空当前选择
        ui->selectedVideoPath->clear();
        currentUploadFilePath.clear();
        ui->uploadButton->setEnabled(false);

        //QTimer.singleShot()延时刷新视频列表
        // 设置定时器，2秒后更新状态并刷新视频列表
        QTimer::singleShot(2000, this, [this]() {
            ui->statusLabel->setText("准备连接服务器..."); // 恢复原始文本
            loadVideoList();                               // 刷新视频列表
        });
    } else {
        QString errorMsg = jsonObj["error"].toString();
        ui->statusLabel->setText("上传失败: " + errorMsg);
        QMessageBox::critical(this, "错误", "视频上传失败:\n" + errorMsg);
    }
}

// 转发连接按钮点击事件
void PlayVideoUI::onConnectButtonClicked()
{
    onConnectClicked();
}

// 处理来自网络的视频列表响应
void PlayVideoUI::onVideoListReceivedFromNetwork(QNetworkReply *reply)
{
    // 只处理视频列表请求
    QString url = reply->url().toString();//获取请求URL
    //contains()判断是否为视频列表请求
    if (url.contains("/videos")) { onVideoListReceived(reply); }    //onVideoListReceived()处理视频列表数据

}

// 处理下载按钮点击事件
void PlayVideoUI::onDownloadButtonClicked()
{
    emitDownloadRequested();
}

// 转发返回按钮点击事件
void PlayVideoUI::onReturnButtonClicked()
{
    onReturnToListClicked();
}

// 处理播放按钮点击事件
void PlayVideoUI::onPlayButtonClicked()
{
    playVideoController->play();
}

// 处理暂停按钮点击事件
void PlayVideoUI::onPauseButtonClicked()
{
    playVideoController->pause();
}

// 处理停止按钮点击事件
void PlayVideoUI::onStopButtonClicked()
{
    playVideoController->stop();
}

// 处理音量滑块变化事件
void PlayVideoUI::onVolumeSliderChanged(int value)
{
    playVideoController->setVolume(value);
}

// 转发浏览按钮点击事件
void PlayVideoUI::onBrowseButtonClicked()
{
    onUploadVideoSelected();
}

// 转发上传按钮点击事件
void PlayVideoUI::onUploadButtonClicked()
{
    onUploadClicked();
}

// 处理视频下载事件
void PlayVideoUI::onVideoDownloadClicked(int index)
{
    if (index < 0 || index >= videoDownloadUrls.size()) { return; }

    QString videoName = videoList[index].first;
    QString downloadUrl = videoDownloadUrls[index];

    // 确保下载URL不是空的
    if (downloadUrl.isEmpty()) {
        QMessageBox::warning(this, "警告", "该视频没有下载链接");
        return;
    }

    // 弹出保存文件对话框
    QString fileName = QFileInfo(downloadUrl).fileName();
    QString savePath = QFileDialog::getSaveFileName(this,
                                                    "保存视频文件",
                                                    QDir::homePath() + "/" + fileName,
                                                    "视频文件 (*.mp4);;所有文件 (*.*)");

    if (savePath.isEmpty()) {
        return; // 用户取消了保存
    }

    // 开始下载
    ui->statusLabel->setText(QString("正在下载: %1").arg(videoName));
    downloadVideo(downloadUrl, savePath);
}

// 下载指定URL的视频文件
void PlayVideoUI::downloadVideo(const QString &downloadUrl, const QString &savePath)
{
    // 构造完整的下载URL
    QUrl url(downloadUrl);
    if (url.isRelative()) {
        // 如果是相对路径，添加服务器地址
        url = QUrl(serverAddress + downloadUrl);
    }

    QNetworkRequest request(url);

    // 发送GET请求下载文件
    QNetworkReply *reply = networkManager->get(request);

    // 创建文件用于保存
    QFile *file = new QFile(savePath);
    if (!file->open(QIODevice::WriteOnly)) {
        ui->statusLabel->setText("无法创建文件");
        QMessageBox::critical(this, "错误", "无法创建文件");
        delete file;
        return;
    }

    // 连接下载进度信号
    connect(reply, &QNetworkReply::downloadProgress, this, [this](qint64 bytesReceived, qint64 bytesTotal) {
        if (bytesTotal > 0) {
            int progress = (bytesReceived * 100) / bytesTotal;
            ui->progressBar->setValue(progress);
            ui->statusLabel->setText(QString("下载进度: %1%%").arg(progress));
        }
    });

    // 连接下载完成信号
    connect(reply, &QNetworkReply::finished, this, [this, reply, file, savePath]() {
        if (reply->error() != QNetworkReply::NoError) {
            ui->statusLabel->setText("下载失败: " + reply->errorString());
            QMessageBox::critical(this, "下载失败", reply->errorString());
            file->close();
            file->deleteLater();
            reply->deleteLater();
            return;
        }

        // 将数据写入文件
        QByteArray data = reply->readAll();
        if (file->write(data) != -1) {
            file->close();
            ui->statusLabel->setText("下载完成");
            ui->progressBar->setValue(100);

            // 询问是否打开文件所在文件夹
            QMessageBox msgBox;
            msgBox.setIcon(QMessageBox::Information);
            msgBox.setText("视频下载完成");
            msgBox.setInformativeText("是否打开文件所在文件夹？");
            msgBox.setStandardButtons(QMessageBox::Yes | QMessageBox::No);
            msgBox.setDefaultButton(QMessageBox::Yes);

            int ret = msgBox.exec();
            if (ret == QMessageBox::Yes) {
                // 打开文件所在文件夹
                QString folderPath = QFileInfo(savePath).absolutePath();
                QDesktopServices::openUrl(QUrl::fromLocalFile(folderPath));
            }
        } else {
            ui->statusLabel->setText("保存文件失败");
            QMessageBox::critical(this, "错误", "保存文件失败");
        }

        file->deleteLater();
        reply->deleteLater();
    });

    // 连接错误信号
    connect(reply, &QNetworkReply::errorOccurred, this, [this](QNetworkReply::NetworkError error) {
        ui->statusLabel->setText("下载失败");
        ui->progressBar->setValue(0);
    });
}

// 触发视频下载请求
void PlayVideoUI::emitDownloadRequested()
{
    // 获取当前播放视频的下载URL
    QString downloadUrl = playVideoController->getDownloadUrl();
    if (!downloadUrl.isEmpty()) {
        // 获取视频名称（从状态标签获取）
        QString statusText = ui->playerStatusLabel->text();
        QString videoName = statusText.startsWith("已选择: ") ? statusText.mid(4) : "unknown";

        // 弹出保存文件对话框
        QString fileName = QFileInfo(downloadUrl).fileName();
        QString savePath = QFileDialog::getSaveFileName(this,
                                                        "保存视频文件",
                                                        QDir::homePath() + "/" + fileName,
                                                        "视频文件 (*.mp4);;所有文件 (*.*)");

        if (!savePath.isEmpty()) {
            // 开始下载
            ui->statusLabel->setText(QString("正在下载: %1").arg(videoName));
            downloadVideo(downloadUrl, savePath);
        }
    } else {
        QMessageBox::warning(this, "警告", "当前视频没有下载链接");
    }
}

// 加载视频列表
void PlayVideoUI::loadVideoList()
{
    QUrl url(serverAddress + "/videos");
    QNetworkRequest request(url);

    // 设置请求头————
    request.setHeader(QNetworkRequest::ContentTypeHeader, "application/json");

    // 发送GET请求
    networkManager->get(request);
}

// 处理视频选择事件
void PlayVideoUI::onVideoSelected(int index)
{
    if (index < 0 || index >= videoList.size()) { return; }

    // 获取选择的视频 URL
    QString videoUrl = serverAddress + videoList[index].second;

    // 获取对应的下载 URL
    QString downloadUrl;
    if (index < videoDownloadUrls.size()) { downloadUrl = videoDownloadUrls[index]; }

    // 使用PlayVideo控制器设置视频源
    playVideoController->setVideoSource(QUrl(videoUrl));

    // 设置下载 URL
    playVideoController->setDownloadUrl(downloadUrl);

    // 启用播放控制按钮
    ui->playButton->setEnabled(true);
    ui->pauseButton->setEnabled(true);
    ui->stopButton->setEnabled(true);

    // 更新状态
    ui->playerStatusLabel->setText("已选择: " + videoList[index].first);

    // 显示视频播放界面
    showVideoPlayer();
}

// 处理接收视频列表响应
void PlayVideoUI::onVideoListReceived(QNetworkReply *reply)
{
    if (reply->error() != QNetworkReply::NoError) {
        ui->statusLabel->setText("连接服务器失败: " + reply->errorString());
        QMessageBox::critical(this, "错误", "无法连接到服务器:\n" + reply->errorString());
        reply->deleteLater();
        return;
    }

    // 读取响应数据
    QByteArray responseData = reply->readAll();
    reply->deleteLater();

    // 解析 JSON
    QJsonDocument jsonDoc = QJsonDocument::fromJson(responseData);
    if (!jsonDoc.isObject()) {
        ui->statusLabel->setText("服务器响应格式错误");
        return;
    }

    QJsonObject jsonObj = jsonDoc.object();
    if (!jsonObj.contains("videos") || !jsonObj["videos"].isArray()) {
        ui->statusLabel->setText("未找到视频列表");
        return;
    }

    QJsonArray videosArray = jsonObj["videos"].toArray();
    clearVideoList();
    videoList.clear();
    videoDetails.clear();
    videoDownloadUrls.clear(); // 清空下载URL列表

    // 反转数组以使最新上传的视频显示在最前面
    QList<QVariant> reversedVideos;
    for (int i = videosArray.size() - 1; i >= 0; --i) {
        reversedVideos.append(videosArray.at(i));
    }

    // 添加到网格布局
    int row = 0, col = 0;
    const int maxCols = 6; // 每行最多6个视频项

    for (int i = 0; i < reversedVideos.size(); ++i) {
        QJsonValue value = reversedVideos[i].toJsonObject();
        if (value.isObject()) {
            QJsonObject videoObj = value.toObject();
            QString name = videoObj["name"].toString();
            QString url = videoObj["url"].toString();
            QString downloadUrl = videoObj["download_url"].toString(); // 获取下载链接
            QString author = videoObj["author"].toString();            // 假设服务器返回作者信息
            QString thumbnail = videoObj["thumbnail"].toString();      // 假设服务器返回缩略图URL

            if (!name.isEmpty() && !url.isEmpty()) {
                // 添加到视频列表
                videoList.append(qMakePair(name, url));
                videoDetails.append(qMakePair(name, author));
                videoDownloadUrls.append(downloadUrl); // 添加到下载URL列表

                // 创建视频项小部件：显示缩略图和名称
                VideoItemWidget *videoItem = new VideoItemWidget(name, thumbnail, this);

                // 设置鼠标悬停样式
                videoItem->setCursor(Qt::PointingHandCursor);

                // 连接点击信号：播放视频
                connect(videoItem, &VideoItemWidget::clicked, this, [this, i]() { onVideoSelected(i); });

                // 添加到网格布局
                ui->videoListLayout->addWidget(videoItem, row, col);

                // 更新行列索引
                col++;
                if (col >= maxCols) {
                    col = 0;
                    row++;
                }
            }
        }
    }

    // 重置所有列的拉伸因子
    for (int i = 0; i < maxCols; ++i) {
        ui->videoListLayout->setColumnStretch(i, 0);
    }
    
    // 如果有视频，给最后一列设置拉伸因子，使所有内容左对齐
    if (!videoList.isEmpty()) {
        ui->videoListLayout->setColumnStretch(maxCols - 1, 1);
    }

    if (videoList.isEmpty()) {
        ui->statusLabel->setText("服务器上没有找到视频");
    } else {
        ui->statusLabel->setText(QString("找到 %1 个视频").arg(videoList.size()));
    }
}

// 处理刷新按钮点击事件
void PlayVideoUI::onRefreshButtonClicked()
{
    if (serverAddress.isEmpty()) {
        QMessageBox::information(this, "提示", "请先连接到服务器");
        return;
    }

    // 更新状态
    ui->statusLabel->setText("正在刷新视频列表...");
    clearVideoList();
    videoList.clear();
    videoDetails.clear();
    videoDownloadUrls.clear();

    // 重新获取视频列表
    loadVideoList();
}
