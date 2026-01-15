//playvideo.cpp
//视频播放状态等，控制器

#include "playvideo.h"
#include "playvideoui.h"
#include <QVideoSink>
#include <QVideoWidget>
#include <QAudioOutput>

// 初始化视频播放控制器
PlayVideo::PlayVideo(QObject *parent)
    : QObject(parent)
    , m_mediaPlayer(new QMediaPlayer(this))
    , m_audioOutput(new QAudioOutput(this))
    , m_uiController(nullptr)
    , m_isPlaying(false)
{
    // 设置音频输出设备
    m_mediaPlayer->setAudioOutput(m_audioOutput);

    // 连接媒体状态变化和位置变化信号
    connect(m_mediaPlayer, &QMediaPlayer::playbackStateChanged, this, &PlayVideo::onPlaybackStateChanged);
    connect(m_mediaPlayer, &QMediaPlayer::positionChanged, this, &PlayVideo::onPositionChanged);
}

PlayVideo::~PlayVideo() {}

// 设置UI控制器,存储UI控制器指针
void PlayVideo::setUIController(PlayVideoUI *uiController)
{
    m_uiController = uiController;

    // UI控制器连接已在UI端完成
    // 此处无需额外连接
}

// 设置视频显示部件
// videoSink()获取视频输出接收器
void PlayVideo::setVideoWidget(QVideoWidget *videoWidget)
{
    if (m_mediaPlayer && videoWidget) { m_mediaPlayer->setVideoOutput(videoWidget->videoSink()); }
}

// 设置视频源
void PlayVideo::setVideoSource(const QUrl &source)
{
    m_mediaPlayer->setSource(source);
    // 启用控制按钮（在UI端处理）
    emit statusChanged("视频源已设置");
}

// 播放视频
void PlayVideo::play()
{
    if (m_mediaPlayer) {
        m_mediaPlayer->play();
        m_isPlaying = true;
        emit playbackStateChanged(true);
        emit statusChanged("正在播放...");
    }
}

// 暂停视频
void PlayVideo::pause()
{
    if (m_mediaPlayer) {
        m_mediaPlayer->pause();
        m_isPlaying = false;
        emit playbackStateChanged(false);
        emit statusChanged("已暂停");
    }
}

// 停止视频
void PlayVideo::stop()
{
    if (m_mediaPlayer) {
        m_mediaPlayer->stop();
        m_isPlaying = false;
        emit playbackStateChanged(false);
        emit statusChanged("已停止");
    }
}

// 设置播放音量
void PlayVideo::setVolume(int volume)
{
    if (m_audioOutput) {
        // 将0-100的值转换为0.0-1.0
        m_audioOutput->setVolume(volume / 100.0);
        emit statusChanged(QString("音量设置为: %1%").arg(volume));
    }
}

// 检查是否正在播放
bool PlayVideo::isPlaying() const
{
    return m_isPlaying;
}

// 枚举判断处理播放状态变化
void PlayVideo::onPlaybackStateChanged(QMediaPlayer::PlaybackState state)
{
    if (!m_uiController) return;

    switch (state) {
    case QMediaPlayer::StoppedState:
        emit statusChanged("播放已停止");
        break;
    case QMediaPlayer::PlayingState:
        emit statusChanged("正在播放...");
        break;
    case QMediaPlayer::PausedState:
        emit statusChanged("已暂停");
        break;
    default:
        break;
    }
}

// 处理播放进度百分比变化
void PlayVideo::onPositionChanged(qint64 position)
{
    if (!m_uiController) return;

    if (m_mediaPlayer->duration() > 0) {
        int progress = (position * 100) / m_mediaPlayer->duration();
        emit progressChanged(progress);
    }
}

// 设置视频下载URL
// 注：UI控制器会处理url,适当时候启用下载按钮
void PlayVideo::setDownloadUrl(const QString &url)
{
    if(m_uiController && !url.isEmpty()) {

    }
    m_downloadUrl = url;
}

// 获取视频下载URL
QString PlayVideo::getDownloadUrl() const
{
    return m_downloadUrl;
}

qint64 PlayVideo::getDuration() const
{
    if (m_mediaPlayer) {
        return m_mediaPlayer->duration();
    }
    return 0;
}

qint64 PlayVideo::getPosition() const
{
    if (m_mediaPlayer) {
        return m_mediaPlayer->position();
    }
    return 0;
}

void PlayVideo::setPosition(qint64 position)
{
    if (m_mediaPlayer) {
        m_mediaPlayer->setPosition(position);
    }
}

// 连接进度信号到UI
void PlayVideo::connectProgressSignal()
{
    if (m_uiController) {
        connect(this, &PlayVideo::progressChanged, m_uiController, [this](int progress) {
            m_uiController->updateProgress(this->getPosition(), this->getDuration());
        });
    }
}
