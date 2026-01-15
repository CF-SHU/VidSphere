//video.cpp

#include "video.h"
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QLabel>
#include <QMouseEvent>
#include <QPainter>
#include <QStyleOption>

// 初始化视频信息显示控件
Video::Video(const QString &title,
             const QString &author,
             const QString &thumbnailUrl,
             const QString &downloadUrl,
             bool showDownloadButton,
             QWidget *parent)
    : QWidget(parent)
    , m_title(title)
    , m_author("UP主: " + author)
    , m_thumbnailUrl(thumbnailUrl)
    , m_downloadUrl(downloadUrl)
    , m_thumbnailLoaded(false)
    , m_showDownloadButton(showDownloadButton)
{
    // 根据是否显示下载按钮设置不同大小
    if (showDownloadButton) {
        setFixedSize(200, 280); // 为按钮留出空间
    } else {
        setFixedSize(200, 250); // 设置固定大小
    }

    setStyleSheet("Video { background-color: #ffffff; border: 1px solid #e0e0e0; border-radius: 8px; }"
                  "Video:hover { background-color: #f5f5f5; border: 1px solid #cccccc; }");

    // 创建布局
    QVBoxLayout *mainLayout = new QVBoxLayout(this);
    mainLayout->setContentsMargins(8, 8, 8, 8);
    mainLayout->setSpacing(8);

    // 缩略图标签
    m_thumbnailLabel = new QLabel(this);
    m_thumbnailLabel->setFixedSize(184, 140); // 留出边距
    m_thumbnailLabel->setStyleSheet("QLabel { background-color: #f0f0f0; border-radius: 4px; }");
    m_thumbnailLabel->setAlignment(Qt::AlignCenter);

    // 如果有缩略图URL，加载缩略图
    if (!thumbnailUrl.isEmpty()) {
        setThumbnail(thumbnailUrl);
    } else {
        // 设置默认缩略图
        m_thumbnailLabel->setText("视频缩略图");
        m_thumbnailLabel->setStyleSheet(
            "QLabel { background-color: #f0f0f0; border-radius: 4px; color: #999999; font-size: 14px; }");
    }

    // 标题标签
    m_titleLabel = new QLabel(title, this);
    m_titleLabel->setWordWrap(true);
    m_titleLabel->setStyleSheet("QLabel { color: #333333; font-size: 14px; font-weight: bold; }");
    m_titleLabel->setMaximumHeight(40);

    mainLayout->addWidget(m_thumbnailLabel);
    mainLayout->addWidget(m_titleLabel);
}

// 设置视频标题，更新标题标签显示
void Video::setTitle(const QString &title)
{
    m_title = title;
    m_titleLabel->setText(title);
}

// 设置视频作者，暂留一个接口，因为没有设置数据库所以没有up信息
void Video::setAuthor(const QString &author)
{
    //m_author = "UP主: " + author;
    //m_authorLabel->setText(m_author);
}

// 设置视频缩略图
void Video::setThumbnail(const QString &thumbnailUrl)
{
    m_thumbnailUrl = thumbnailUrl;//缩略图URL

    m_thumbnailLabel->setText("加载中...");
    m_thumbnailLabel->setStyleSheet(
        "QLabel { background-color: #f0f0f0; border-radius: 4px; color: #999999; font-size: 12px; }");

    // 调用QPainter绘制缩略图内容，QPixmap.fill()创建占位符图像（默认缩略图）
    QPixmap placeholder(184, 140);
    placeholder.fill(Qt::lightGray);
    QPainter painter(&placeholder);
    painter.setPen(QPen(Qt::darkGray, 2));
    painter.drawRect(0, 0, 183, 139);
    painter.drawText(placeholder.rect(), Qt::AlignCenter, "视频缩略图");

    //setPixmap()设置缩略图显示
    m_thumbnailPixmap = placeholder;
    m_thumbnailLabel->setPixmap(m_thumbnailPixmap.scaled(184, 140, Qt::KeepAspectRatio, Qt::SmoothTransformation));
    m_thumbnailLoaded = true;
}

// 处理鼠标左键点击
void Video::mousePressEvent(QMouseEvent *event)
{
    if (event->button() == Qt::LeftButton) { emit clicked(); }
    QWidget::mousePressEvent(event);
}

// 设置视频下载URL
void Video::setDownloadUrl(const QString &downloadUrl)
{
    m_downloadUrl = downloadUrl;
}

// 处理绘制事件————————？？
void Video::paintEvent(QPaintEvent *event)
{
    QStyleOption opt;
    opt.initFrom(this);//初始化样式选项
    QPainter p(this);
    style()->drawPrimitive(QStyle::PE_Widget, &opt, &p, this);//绘制基本控件样式
    QWidget::paintEvent(event);
}
