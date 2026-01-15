//downloadvideowidge.h
//视频下载，继承Video类，专门用于可下载视频的显示，包含下载按钮

#pragma once

#include "video.h"
#include <QPushButton>

class DownloadVideoWidget : public Video
{
    Q_OBJECT

public:
    explicit DownloadVideoWidget(const QString &title,
                                 const QString &author,
                                 const QString &thumbnailUrl,
                                 const QString &downloadUrl,
                                 QWidget *parent = nullptr);

    QString getDownloadUrl() const { return m_downloadUrl; }

signals:
    void downloadClicked(); // 新增下载点击信号

private:
    QString m_downloadUrl;
    QPushButton *m_downloadButton;
};
