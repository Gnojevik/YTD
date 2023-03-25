from PyQt6.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox
import sys
import re
import os
from pytube import exceptions, YouTube
from moviepy.video.io.VideoFileClip import AudioFileClip
from SaveDirectory import Ui_MainWindow
#from loger import MyLogger
from proglog import ProgressBarLogger


class MyLogger(ProgressBarLogger):

    def __init__(self, window):
        super().__init__()
        self.window = window

    def callback(self, **changes):
        for (parameter, value) in changes.items():
            print (f"{value}")

    def bars_callback(self, bar, attr, value, old_value=None):
        percentage = (value / self.bars[bar]['total']) * 100
        #print(f"percentage: {int(percentage)}")
        
         
        self.window.updateProgressBar(int(percentage)) 
        

class testWindow(QMainWindow, Ui_MainWindow):
    
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.show()

        self.actionsave_Directory.triggered.connect(self.click)
        self.pushButton.clicked.connect(self.click)
        self.lineEdit.textEdited.connect(self.text_edited)
        self.comboBox.currentIndexChanged.connect(self.current_index)
        self.progressBar.setVisible(False)
        self.comboBox.setVisible(False)
        self.label_2.setVisible(False)
        self.label_3.setVisible(False)

        self.logger = MyLogger(self)
        
    link = ''
    index = 0

    
    def text_edited(self, s):

        self.pushButton.setEnabled(True)
        self.actionsave_Directory.setEnabled(True)
        self.comboBox.setVisible(True)
        self.label_2.setVisible(True)
        self.link = s
        
    
    def save_dir(self):
        path = QFileDialog.getExistingDirectory()
        return path

    def click(self, link):
        self.info_video(self.link, self.index)
        
                

    def current_index(self):
        self.index = self.comboBox.currentIndex()
        
        

    def info_video(self, link, quality):
        outputpath = self.save_dir()
        try:
            video = YouTube(link, on_progress_callback=self.progress_func)

        except exceptions.RegexMatchError:
            QMessageBox.warning(self, 'Warning', "не правильно введене посилання на відео" )
            e = "не правильно введене посилання на відео"
            return e
        except exceptions.MembersOnly:
            QMessageBox.warning(self, 'Warning', "Відео доступне лише для підписників")
            e = "Відео доступне лише для підписників"
            return e
        else: 
            
            if quality == 0:
                output = video.streams.get_highest_resolution()   
                output.download(output_path = outputpath)
                
            if quality == 1:
                output = video.streams.get_lowest_resolution() 
                output.download(output_path = outputpath)
            if quality == 2:
                audio_streams = video.streams.filter(only_audio=True)
            
                # знайдіть найвищу якість за бітрейтом
                highest_bitrate = 0
                highest_bitrate_stream = None
                for stream in audio_streams:
                    if stream.abr is not None:
                        # використовуємо регулярний вираз, щоб виділити значення бітрейту
                        abr_match = re.search(r'(\d+)kbps', stream.abr)
                        if abr_match:
                            abr = int(abr_match.group(1))
                            if abr > highest_bitrate:
                                highest_bitrate = abr
                                highest_bitrate_stream = stream

                
                # завантажте аудіо стрім з найвищим бітрейтом
                if highest_bitrate_stream is not None:
                    file_name = f"{video.title}.mp4"
                    file_name = file_name.replace("/", "_") if "/" in file_name else file_name
                    highest_bitrate_stream.download(filename=file_name, output_path = outputpath)

                    # сконвертувати аудіо в mp3
                    
                    
                    audio = AudioFileClip(f"{outputpath}/{file_name}")
                    audio.write_audiofile(f"{outputpath}/{file_name}.mp3", verbose=False, logger=self.logger)
                    audio.close()
                    

                    #видалення файла .mp4
                    self.label_3.setText('delet mp4 ...')
                    os.remove(f"{outputpath}/{file_name}")
                    self.label_3.setText('done!')
                    QMessageBox.information(self, 'information', f""" {stream.title} \n \n Успішно сконвертовано  """ )
                    self.label_3.setVisible(False)
                    self.progressBar.setVisible(False)
                    
                else:
                    QMessageBox.warning(self, 'Warning', "Не вдалося знайти аудіо стрім з найвищим бітрейтом.")

                
                   
                   

            
                 
                  
    def progress_func(self, stream, value, bytes_remaining):
            size = stream.filesize 
            progress = round(((float(abs(bytes_remaining-size)/size))*float(100)))
            self.progressBar.setVisible(True)
            self.progressBar.setFormat("Download: %p%")
            self.progressBar.setValue(progress)
            if progress == 100 and self.index != 2:
                QMessageBox.information(self, 'information', f""" {stream.title} \n \n Успішно скачано  """ )
                self.progressBar.setValue(0)
                self.progressBar.setVisible(False)
            
            
               
    def updateProgressBar(self, value):
        self.progressBar.setVisible(True)
        self.progressBar.setFormat("Convert to mp3: %p%")
        self.progressBar.setValue(value)
    
            
    

app = QApplication(sys.argv)
test = testWindow()
sys.exit(app.exec())