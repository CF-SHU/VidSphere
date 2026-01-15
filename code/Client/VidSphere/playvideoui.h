//playvideoui.h
//视频流客户端主界面控制器，管理视频列表显示、视频播放控制、服务器连接、视频上传下载等
//视频列表界面和视频播放界面两个主要界面

#pragma once

#include <QMainWindow>
#include <QNetworkAccessManager>
#include <QNetworkReply>
#include <QMediaPlayer>
#include <QVideoWidget>
#include <QAudioOutput>
#include <QScrollArea>
#include <QGridLayout>
#include <QStackedWidget>
#include <QToolButton>
#include <QPushButton>
#include <QLineEdit>
#include <QSlider>
#include <QLabel>
#include <QVBoxLayout>
#include <QMouseEvent>

QT_BEGIN_NAMESPACE
namespace Ui {
    class PlayVideoUI;
}
QT_END_NAMESPACE

class Video;
class DownloadVideoWidget;
class PlayVideo;

// 自定义视频项控件，显示缩略图和名称
class VideoItemWidget : public QWidget
{
    Q_OBJECT

public:
    explicit VideoItemWidget(const QString &name, const QString &thumbnail, QWidget *parent = nullptr)
        : QWidget(parent)
        , m_name(name)
        , m_thumbnail(thumbnail)
    {
        setFixedSize(120, 120); // 增加高度以容纳名称

        QVBoxLayout *layout = new QVBoxLayout(this);
        layout->setSpacing(5);
        layout->setContentsMargins(2, 2, 2, 2);

        m_thumbnailLabel = new QLabel(this);
        m_thumbnailLabel->setFixedSize(116, 90);
        m_thumbnailLabel->setStyleSheet("border: 1px solid gray; background-color: lightgray;");
        m_thumbnailLabel->setAlignment(Qt::AlignCenter);

        m_nameLabel = new QLabel(name, this);
        m_nameLabel->setWordWrap(true);
        m_nameLabel->setAlignment(Qt::AlignCenter);
        m_nameLabel->setStyleSheet("font-size: 9px; color: black;");

        layout->addWidget(m_thumbnailLabel);
        layout->addWidget(m_nameLabel);

        setCursor(Qt::PointingHandCursor);

        // 如果有缩略图URL，则加载图片，否则显示占位符（默认格式）
        if (!thumbnail.isEmpty()) {
            m_thumbnailLabel->setText("视频");
        } else {
            m_thumbnailLabel->setText("视频");
        }
    }

signals:
    void clicked();

protected:
    void mousePressEvent(QMouseEvent *event) override
    {
        if (event->button() == Qt::LeftButton) { emit clicked(); }
        QWidget::mousePressEvent(event);
    }

private:
    QString m_name;
    QString m_thumbnail;
    QLabel *m_thumbnailLabel;
    QLabel *m_nameLabel;
};

class PlayVideoUI : public QMainWindow
{
    Q_OBJECT

public:
    PlayVideoUI(QWidget *parent = nullptr);
    ~PlayVideoUI();

private slots:
    void onConnectClicked();//连接服务器
    void onVideoListReceived(QNetworkReply *reply);//接收视频列表
    void onVideoSelected(int index = -1);//选择视频
    void onReturnToListClicked();//返回视频列表
    void onUploadClicked();//上传视频
    void onUploadVideoSelected();//选择要上传的视频
    void onVideoUploaded(QNetworkReply *reply);//视频上传完成
    void onVideoDownloadClicked(int index);//下载视频
    void onConnectButtonClicked();//连接按钮点击
    void onVideoListReceivedFromNetwork(QNetworkReply *reply); //网络收到视频列表
    void onDownloadButtonClicked();
    void onReturnButtonClicked();
    void onPlayButtonClicked();
    void onPauseButtonClicked();
    void onStopButtonClicked();
    void onVolumeSliderChanged(int value);//音量滑块变化
    void onBrowseButtonClicked();
    void onUploadButtonClicked();
    void onRefreshButtonClicked();

private:
    void loadVideoList();//加载视频列表
    void showVideoList();//显示视频列表界面
    void showVideoPlayer();//显示视频播放界面
    void clearVideoList();//清空视频列表
    void downloadVideo(const QString &downloadUrl, const QString &filename);//下载视频
    void emitDownloadRequested();//发出下载请求信号

    Ui::PlayVideoUI *ui;
    QNetworkAccessManager *networkManager;
    PlayVideo *playVideoController;
    QString serverAddress;                       //服务器地址
    QList<QPair<QString, QString>> videoList;    //视频列表 (名称, URL)
    QList<QPair<QString, QString>> videoDetails; //视频详细信息 (标题, 作者)
    QString currentUploadFilePath;               //当前上传的文件路径
    QList<QString> videoDownloadUrls;            //视频下载URL列表
};
