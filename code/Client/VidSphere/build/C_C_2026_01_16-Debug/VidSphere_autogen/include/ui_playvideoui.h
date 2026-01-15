/********************************************************************************
** Form generated from reading UI file 'playvideoui.ui'
**
** Created by: Qt User Interface Compiler version 6.9.1
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef UI_PLAYVIDEOUI_H
#define UI_PLAYVIDEOUI_H

#include <QtCore/QVariant>
#include <QtMultimediaWidgets/QVideoWidget>
#include <QtWidgets/QApplication>
#include <QtWidgets/QGridLayout>
#include <QtWidgets/QGroupBox>
#include <QtWidgets/QHBoxLayout>
#include <QtWidgets/QLabel>
#include <QtWidgets/QLineEdit>
#include <QtWidgets/QMainWindow>
#include <QtWidgets/QProgressBar>
#include <QtWidgets/QPushButton>
#include <QtWidgets/QScrollArea>
#include <QtWidgets/QSlider>
#include <QtWidgets/QSpacerItem>
#include <QtWidgets/QStackedWidget>
#include <QtWidgets/QToolButton>
#include <QtWidgets/QVBoxLayout>
#include <QtWidgets/QWidget>

QT_BEGIN_NAMESPACE

class Ui_PlayVideoUI
{
public:
    QWidget *centralwidget;
    QVBoxLayout *mainLayout;
    QStackedWidget *mainStackedWidget;
    QWidget *videoListPage;
    QVBoxLayout *listPageLayout;
    QGroupBox *serverGroupBox;
    QHBoxLayout *serverLayout;
    QLabel *serverLabel;
    QLineEdit *serverInput;
    QPushButton *connectButton;
    QSpacerItem *serverHorizontalSpacer;
    QGroupBox *uploadGroupBox;
    QHBoxLayout *uploadLayout;
    QLineEdit *selectedVideoPath;
    QPushButton *browseButton;
    QPushButton *uploadButton;
    QScrollArea *videoListScrollArea;
    QWidget *videoListContentWidget;
    QGridLayout *videoListLayout;
    QHBoxLayout *statusLayout;
    QLabel *statusLabel;
    QPushButton *refreshButton;
    QProgressBar *progressBar;
    QWidget *videoPlayerPage;
    QVBoxLayout *playerPageLayout;
    QHBoxLayout *topToolBarLayout;
    QToolButton *returnButton;
    QSpacerItem *topRightSpacer;
    QPushButton *downloadButton;
    QVideoWidget *videoWidget;
    QHBoxLayout *controlLayout;
    QPushButton *playButton;
    QPushButton *pauseButton;
    QPushButton *stopButton;
    QSpacerItem *controlHorizontalSpacer;
    QLabel *volumeLabel;
    QSlider *volumeSlider;
    QSpacerItem *controlRightSpacer;
    QHBoxLayout *progressLayout;
    QLabel *currentTimeLabel;
    QSlider *progressSlider;
    QLabel *totalTimeLabel;

    void setupUi(QMainWindow *PlayVideoUI)
    {
        if (PlayVideoUI->objectName().isEmpty())
            PlayVideoUI->setObjectName("PlayVideoUI");
        PlayVideoUI->resize(1000, 700);
        centralwidget = new QWidget(PlayVideoUI);
        centralwidget->setObjectName("centralwidget");
        mainLayout = new QVBoxLayout(centralwidget);
        mainLayout->setObjectName("mainLayout");
        mainStackedWidget = new QStackedWidget(centralwidget);
        mainStackedWidget->setObjectName("mainStackedWidget");
        videoListPage = new QWidget();
        videoListPage->setObjectName("videoListPage");
        listPageLayout = new QVBoxLayout(videoListPage);
        listPageLayout->setObjectName("listPageLayout");
        serverGroupBox = new QGroupBox(videoListPage);
        serverGroupBox->setObjectName("serverGroupBox");
        serverLayout = new QHBoxLayout(serverGroupBox);
        serverLayout->setObjectName("serverLayout");
        serverLabel = new QLabel(serverGroupBox);
        serverLabel->setObjectName("serverLabel");

        serverLayout->addWidget(serverLabel);

        serverInput = new QLineEdit(serverGroupBox);
        serverInput->setObjectName("serverInput");

        serverLayout->addWidget(serverInput);

        connectButton = new QPushButton(serverGroupBox);
        connectButton->setObjectName("connectButton");

        serverLayout->addWidget(connectButton);

        serverHorizontalSpacer = new QSpacerItem(40, 20, QSizePolicy::Policy::Expanding, QSizePolicy::Policy::Minimum);

        serverLayout->addItem(serverHorizontalSpacer);


        listPageLayout->addWidget(serverGroupBox);

        uploadGroupBox = new QGroupBox(videoListPage);
        uploadGroupBox->setObjectName("uploadGroupBox");
        uploadLayout = new QHBoxLayout(uploadGroupBox);
        uploadLayout->setObjectName("uploadLayout");
        selectedVideoPath = new QLineEdit(uploadGroupBox);
        selectedVideoPath->setObjectName("selectedVideoPath");
        selectedVideoPath->setReadOnly(true);

        uploadLayout->addWidget(selectedVideoPath);

        browseButton = new QPushButton(uploadGroupBox);
        browseButton->setObjectName("browseButton");

        uploadLayout->addWidget(browseButton);

        uploadButton = new QPushButton(uploadGroupBox);
        uploadButton->setObjectName("uploadButton");
        uploadButton->setEnabled(false);

        uploadLayout->addWidget(uploadButton);


        listPageLayout->addWidget(uploadGroupBox);

        videoListScrollArea = new QScrollArea(videoListPage);
        videoListScrollArea->setObjectName("videoListScrollArea");
        videoListScrollArea->setVerticalScrollBarPolicy(Qt::ScrollBarPolicy::ScrollBarAsNeeded);
        videoListScrollArea->setHorizontalScrollBarPolicy(Qt::ScrollBarPolicy::ScrollBarAsNeeded);
        videoListScrollArea->setWidgetResizable(true);
        videoListContentWidget = new QWidget();
        videoListContentWidget->setObjectName("videoListContentWidget");
        videoListContentWidget->setGeometry(QRect(0, 0, 946, 410));
        videoListLayout = new QGridLayout(videoListContentWidget);
        videoListLayout->setSpacing(10);
        videoListLayout->setObjectName("videoListLayout");
        videoListLayout->setSizeConstraint(QLayout::SetMinAndMaxSize);
        videoListLayout->setContentsMargins(10, 10, 10, 10);
        videoListScrollArea->setWidget(videoListContentWidget);

        listPageLayout->addWidget(videoListScrollArea);

        statusLayout = new QHBoxLayout();
        statusLayout->setObjectName("statusLayout");
        statusLabel = new QLabel(videoListPage);
        statusLabel->setObjectName("statusLabel");

        statusLayout->addWidget(statusLabel);

        refreshButton = new QPushButton(videoListPage);
        refreshButton->setObjectName("refreshButton");

        statusLayout->addWidget(refreshButton);

        progressBar = new QProgressBar(videoListPage);
        progressBar->setObjectName("progressBar");
        progressBar->setValue(0);

        statusLayout->addWidget(progressBar);


        listPageLayout->addLayout(statusLayout);

        mainStackedWidget->addWidget(videoListPage);
        videoPlayerPage = new QWidget();
        videoPlayerPage->setObjectName("videoPlayerPage");
        playerPageLayout = new QVBoxLayout(videoPlayerPage);
        playerPageLayout->setObjectName("playerPageLayout");
        topToolBarLayout = new QHBoxLayout();
        topToolBarLayout->setObjectName("topToolBarLayout");
        returnButton = new QToolButton(videoPlayerPage);
        returnButton->setObjectName("returnButton");

        topToolBarLayout->addWidget(returnButton);

        topRightSpacer = new QSpacerItem(40, 20, QSizePolicy::Policy::Expanding, QSizePolicy::Policy::Minimum);

        topToolBarLayout->addItem(topRightSpacer);

        downloadButton = new QPushButton(videoPlayerPage);
        downloadButton->setObjectName("downloadButton");

        topToolBarLayout->addWidget(downloadButton);


        playerPageLayout->addLayout(topToolBarLayout);

        videoWidget = new QVideoWidget(videoPlayerPage);
        videoWidget->setObjectName("videoWidget");
        videoWidget->setMinimumSize(QSize(640, 480));

        playerPageLayout->addWidget(videoWidget);

        controlLayout = new QHBoxLayout();
        controlLayout->setObjectName("controlLayout");
        playButton = new QPushButton(videoPlayerPage);
        playButton->setObjectName("playButton");

        controlLayout->addWidget(playButton);

        pauseButton = new QPushButton(videoPlayerPage);
        pauseButton->setObjectName("pauseButton");

        controlLayout->addWidget(pauseButton);

        stopButton = new QPushButton(videoPlayerPage);
        stopButton->setObjectName("stopButton");

        controlLayout->addWidget(stopButton);

        controlHorizontalSpacer = new QSpacerItem(40, 20, QSizePolicy::Policy::Expanding, QSizePolicy::Policy::Minimum);

        controlLayout->addItem(controlHorizontalSpacer);

        volumeLabel = new QLabel(videoPlayerPage);
        volumeLabel->setObjectName("volumeLabel");

        controlLayout->addWidget(volumeLabel);

        volumeSlider = new QSlider(videoPlayerPage);
        volumeSlider->setObjectName("volumeSlider");
        volumeSlider->setMaximum(100);
        volumeSlider->setValue(50);
        volumeSlider->setOrientation(Qt::Orientation::Horizontal);

        controlLayout->addWidget(volumeSlider);

        controlRightSpacer = new QSpacerItem(40, 20, QSizePolicy::Policy::Expanding, QSizePolicy::Policy::Minimum);

        controlLayout->addItem(controlRightSpacer);


        playerPageLayout->addLayout(controlLayout);

        progressLayout = new QHBoxLayout();
        progressLayout->setObjectName("progressLayout");
        currentTimeLabel = new QLabel(videoPlayerPage);
        currentTimeLabel->setObjectName("currentTimeLabel");

        progressLayout->addWidget(currentTimeLabel);

        progressSlider = new QSlider(videoPlayerPage);
        progressSlider->setObjectName("progressSlider");
        progressSlider->setOrientation(Qt::Horizontal);
        progressSlider->setMinimum(0);
        progressSlider->setMaximum(100);

        progressLayout->addWidget(progressSlider);

        totalTimeLabel = new QLabel(videoPlayerPage);
        totalTimeLabel->setObjectName("totalTimeLabel");

        progressLayout->addWidget(totalTimeLabel);


        playerPageLayout->addLayout(progressLayout);

        mainStackedWidget->addWidget(videoPlayerPage);

        mainLayout->addWidget(mainStackedWidget);

        PlayVideoUI->setCentralWidget(centralwidget);

        retranslateUi(PlayVideoUI);

        QMetaObject::connectSlotsByName(PlayVideoUI);
    } // setupUi

    void retranslateUi(QMainWindow *PlayVideoUI)
    {
        PlayVideoUI->setWindowTitle(QCoreApplication::translate("PlayVideoUI", "\350\247\206\351\242\221\346\265\201\345\256\242\346\210\267\347\253\257", nullptr));
        serverGroupBox->setTitle(QCoreApplication::translate("PlayVideoUI", "\346\234\215\345\212\241\345\231\250\350\277\236\346\216\245", nullptr));
        serverLabel->setText(QCoreApplication::translate("PlayVideoUI", "\346\234\215\345\212\241\345\231\250\345\234\260\345\235\200:", nullptr));
        serverInput->setText(QCoreApplication::translate("PlayVideoUI", "http://localhost:5000", nullptr));
        connectButton->setText(QCoreApplication::translate("PlayVideoUI", "\350\277\236\346\216\245", nullptr));
        uploadGroupBox->setTitle(QCoreApplication::translate("PlayVideoUI", "\344\270\212\344\274\240\350\247\206\351\242\221", nullptr));
        selectedVideoPath->setPlaceholderText(QCoreApplication::translate("PlayVideoUI", "\350\257\267\351\200\211\346\213\251\350\247\206\351\242\221\346\226\207\344\273\266...", nullptr));
        browseButton->setText(QCoreApplication::translate("PlayVideoUI", "\346\265\217\350\247\210", nullptr));
        uploadButton->setText(QCoreApplication::translate("PlayVideoUI", "\344\270\212\344\274\240", nullptr));
        statusLabel->setText(QCoreApplication::translate("PlayVideoUI", "\345\207\206\345\244\207\350\277\236\346\216\245\346\234\215\345\212\241\345\231\250...", nullptr));
        refreshButton->setText(QCoreApplication::translate("PlayVideoUI", "\345\210\267\346\226\260", nullptr));
        returnButton->setText(QCoreApplication::translate("PlayVideoUI", "\342\206\220 \350\277\224\345\233\236", nullptr));
        downloadButton->setText(QCoreApplication::translate("PlayVideoUI", "\344\270\213\350\275\275", nullptr));
        playButton->setText(QCoreApplication::translate("PlayVideoUI", "\346\222\255\346\224\276", nullptr));
        pauseButton->setText(QCoreApplication::translate("PlayVideoUI", "\346\232\202\345\201\234", nullptr));
        stopButton->setText(QCoreApplication::translate("PlayVideoUI", "\345\201\234\346\255\242", nullptr));
        volumeLabel->setText(QCoreApplication::translate("PlayVideoUI", "\351\237\263\351\207\217:", nullptr));
        currentTimeLabel->setText(QCoreApplication::translate("PlayVideoUI", "00:00", nullptr));
        totalTimeLabel->setText(QCoreApplication::translate("PlayVideoUI", "00:00", nullptr));
    } // retranslateUi

};

namespace Ui {
    class PlayVideoUI: public Ui_PlayVideoUI {};
} // namespace Ui

QT_END_NAMESPACE

#endif // UI_PLAYVIDEOUI_H
