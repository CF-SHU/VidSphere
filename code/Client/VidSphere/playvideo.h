//playvideo.h
//负责与QMediaPlayer交互，管理视频播放状态，并提供接口给UI控制器

#pragma once

#include <QObject>
#include <QMediaPlayer>
#include <QAudioOutput>
#include <QVideoSink>
#include <QUrl>
#include <QVideoWidget>

class PlayVideoUI;

class PlayVideo : public QObject
{
    Q_OBJECT

public:
    explicit PlayVideo(QObject *parent = nullptr);
    ~PlayVideo();

    // 设置UI控制器
    void setUIController(PlayVideoUI *uiController);

    void setVideoWidget(QVideoWidget *videoWidget);
    void setVideoSource(const QUrl &source);

    void play();
    void pause();
    void stop();
    void setVolume(int volume);
    void setDownloadUrl(const QString &url);
    QString getDownloadUrl() const;

    bool isPlaying() const;
    qint64 getDuration() const;
    qint64 getPosition() const;
    void setPosition(qint64 position);

    // 连接进度信号到UI
    void connectProgressSignal();

signals:
    void statusChanged(const QString &message);
    void progressChanged(int value);
    void playbackStateChanged(bool playing);

private slots:
    void onPlaybackStateChanged(QMediaPlayer::PlaybackState state);
    void onPositionChanged(qint64 position);

private:
    QMediaPlayer *m_mediaPlayer;
    QAudioOutput *m_audioOutput;
    PlayVideoUI *m_uiController;
    bool m_isPlaying;
    QString m_downloadUrl;
};
