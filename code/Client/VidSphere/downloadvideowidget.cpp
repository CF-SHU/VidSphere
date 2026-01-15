//downloadvideowidget.cpp
// 视频下载+界面

#include "downloadvideowidget.h"
#include <QVBoxLayout>
#include <QHBoxLayout>

DownloadVideoWidget::DownloadVideoWidget(const QString &title,
                                         const QString &author,
                                         const QString &thumbnailUrl,
                                         const QString &downloadUrl,
                                         QWidget *parent)
    : Video(title, author, thumbnailUrl, downloadUrl, true, parent)
    , m_downloadUrl(downloadUrl)
{
    // 重设大小，为按钮留出空间
    setFixedSize(200, 280);

    // 在父类布局的基础上添加下载按钮,qobject_cast()获取父类布局
    QVBoxLayout *mainLayout = qobject_cast<QVBoxLayout *>(layout());
    if (mainLayout) {
        // 创建下载按钮
        m_downloadButton = new QPushButton("下载", this);
        m_downloadButton->setFixedHeight(30);

        //调用QWidget.setStyleSheet()设置按钮样式
        m_downloadButton->setStyleSheet("QPushButton { background-color: #4CAF50; color: white; border: none; "
                                        "border-radius: 4px; font-size: 12px; font-weight: bold; }"
                                        "QPushButton:hover { background-color: #45a049; }"
                                        "QPushButton:pressed { background-color: #3d8b40; }");

        // 连接下载按钮信号
        connect(m_downloadButton, &QPushButton::clicked, this, [this]() { emit downloadClicked(); });

        mainLayout->addWidget(m_downloadButton);
    }
}
