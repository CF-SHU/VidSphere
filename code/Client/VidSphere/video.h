//video.h
//显示视频缩略图、标题、作者信息，并提供（鼠标）视频点击和下载功能

#pragma once

#include <QWidget>
#include <QLabel>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QMouseEvent>
#include <QPixmap>
#include <QPainter>
#include <QPushButton>

class Video : public QWidget
{
    Q_OBJECT

public:
    explicit Video(const QString &title = "",
                   const QString &author = "",
                   const QString &thumbnailUrl = "",
                   const QString &downloadUrl = "",
                   bool showDownloadButton = false,
                   QWidget *parent = nullptr);

    void setTitle(const QString &title);
    void setAuthor(const QString &author);
    void setThumbnail(const QString &thumbnailUrl);
    void setDownloadUrl(const QString &downloadUrl);
    void setShowDownloadButton(bool show);

    QString getTitle() const { return m_title; }
    QString getAuthor() const { return m_author; }
    QString getThumbnailUrl() const { return m_thumbnailUrl; }
    QString getDownloadUrl() const { return m_downloadUrl; }

signals:
    void clicked();
    void downloadClicked();

protected:
    void mousePressEvent(QMouseEvent *event) override;
    void paintEvent(QPaintEvent *event) override;

private:
    QString m_title;
    QString m_author;
    QString m_thumbnailUrl;
    QString m_downloadUrl;
    QPixmap m_thumbnailPixmap;
    QLabel *m_thumbnailLabel;
    QLabel *m_titleLabel;
    QLabel *m_authorLabel;
    QPushButton *m_downloadButton;
    bool m_thumbnailLoaded;
    bool m_showDownloadButton;
};
