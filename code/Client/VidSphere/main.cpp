//main.cpp

#include "playvideoui.h"

#include <QApplication>

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    PlayVideoUI w;
    w.show();
    return a.exec();
}
