import telebot
import os
import subprocess
import cv2
import re
import FaceDetector
token = "1311274358:AAGcCioU_6hBzedZa42FJ8bfDOuX7DEFB7s"
detector = FaceDetector.FaceDetector()
bot = telebot.TeleBot(token)

def downloadFile(fileId):
    return bot.download_file(bot.get_file(fileId).file_path)

@bot.message_handler(content_types=['photo'])
def getPhoto(message):
    bot.send_message(message.chat.id, 'Вы прислали фото')

    userDir,photoFilesList = getFilesList('./photo/', message.from_user.id)

    photoBytes = downloadFile(message.photo[-1].file_id)
    tmpFilePath = userDir+'test.jpg'
    with open(tmpFilePath,'wb') as file :
        file.write(photoBytes)

    image, faceLocations = detector.detectFaceWithMTCNN(tmpFilePath)#detectFaceWithCascades(tmpFilePath)#
    faceQuantity = len(faceLocations)
    cv2.imwrite(userDir+'testWithMarker.jpg',image)
    if (faceQuantity == 0):
        bot.send_message(message.chat.id, "На фотографии лица не обнаружены", reply_to_message_id=message.message_id)
        os.remove(tmpFilePath)
    else:
        photosQuantity = len(photoFilesList)
        os.rename(tmpFilePath,userDir+f"photo_{photosQuantity}.jpg")
        bot.send_photo(message.chat.id,photo=open(userDir+'testWithMarker.jpg','rb'),caption=f"На фотографии обнаружены лица ({faceQuantity} шт.)")
        bot.send_message(message.chat.id, f"Вы прислали {photosQuantity+1} фото, на которых есть лица")
        os.remove(userDir+'testWithMarker.jpg')


@bot.message_handler(content_types=['voice'])
def getAudio(message):
    bot.send_message(message.chat.id, 'Вы прислали аудиосообщение')
    audioNumber,newFilePath = saveAudio(message.from_user.id,message.voice.file_id)
    bot.send_document(message.chat.id,data=open(newFilePath,'rb'))
    # bot.send_audio(message.chat.id,audio=open(newFilePath,'rb'))
    bot.send_message(message.chat.id, f'Это ваше {audioNumber} аудиосообщение')

def checkUserDir(path,userId):
    usersDir = os.listdir(path)
    userDir = path + str(userId) + '/'
    if str(userId) not in usersDir:
        os.mkdir(userDir)
    return userDir

def saveAudio(userId, voiceId):
    userDir,audioFilesList = getFilesList('./audio/',userId)
    filesQuantity = len(audioFilesList)
    voiceBytes =  downloadFile(voiceId)

    newFilePath = userDir+f"audio_message_{filesQuantity}.wav"
    command = [
              r'D:\ffmpeg-20200720-43a08d9-win64-static\bin\ffmpeg.exe',
                 '-i', "pipe:0",
                '-ar', '16000',
                newFilePath
    ]
    proc = subprocess.Popen(command,stdin=subprocess.PIPE,stderr=subprocess.DEVNULL)
    proc.stdin.write(voiceBytes)
    proc.stdin.close()
    proc.wait()
    return (filesQuantity+1,newFilePath)

def getFilesList(dir,userId):
    userDir = checkUserDir(dir, userId)
    return (userDir,os.listdir(userDir))


def sendFilesList(message,dir):
    _,audioFilesList = getFilesList(dir,message.from_user.id)
    if len(audioFilesList) == 0:
        bot.send_message(message.chat.id, "Ничего не найдено")
    else:
        bot.send_message(message.chat.id, "\n".join(audioFilesList))
        bot.send_message(message.chat.id, "какой файл отправить?")

@bot.message_handler(commands=['start','help','listphoto','listaudio'])
def commands_message(message):
    if message.text == "/start":
        bot.send_message(message.chat.id, 'Приветствую. Я тестовый телеграмм бот. Напишите /help, чтобы получить справку.')
    elif message.text == "/help":
        text = """
Данный бот может конвертировать аудиосообщения из ogg формата в wav. 
Для этого необходимо записать свой голос и отправить его боту.
В ответ он пришлет аудио в формате wav.
Также бот может на фотографиях отмечать лица. 
Чтобы воспользоваться этой функцией необходимо просто отправить фотографию.
Дополнительные команды:
/listaudio - получить список ранее отправленных аудиосообщений;
/listphoto - получить список фотографий, на которых были обнаружены лица.
Если вы хотите скачать файл из списка, то просто отправьте его название.
Например: photo_0.jpg
"""
        bot.send_message(message.chat.id, text)
    elif message.text == "/listaudio":
        sendFilesList(message,"./audio/")
    elif message.text == "/listphoto":
        sendFilesList(message,"./photo/")

@bot.message_handler(content_types=['text'])
def text_message(message):
    messageText = message.text.lower()
    fileList = re.findall(r"(audio_message_[\d]+\.wav|photo_[\d]+\.jpg)", messageText)
    if len(fileList) != 0:
        photoDir,photoFilesList = getFilesList("./photo/",message.from_user.id)
        audioDir,audioFilesList = getFilesList("./audio/",message.from_user.id)
        for fileName in fileList:
            if fileName.find("audio") != -1:
                if fileName in audioFilesList:
                    bot.send_document(message.chat.id,data=open(audioDir+fileName,"rb"))
                else:
                    bot.send_message(message.chat.id,fileName+" не существует")
            elif fileName.find("photo") != -1:
                if fileName in photoFilesList:
                    bot.send_document(message.chat.id,data=open(photoDir+fileName,"rb"))
                else:
                    bot.send_message(message.chat.id,fileName+"не существует")
    else:
        bot.send_message(message.chat.id, messageText)

def checkDataStorage():
    dirs = os.listdir('./')
    def checkDir(dirPath):
        if dirPath not in dirs:
            os.mkdir(dirPath)
    checkDir("audio")
    checkDir("photo")

if __name__ == "__main__":
    checkDataStorage()
    bot.polling()


    # det = FaceDetector.FaceDetector()
    # det.detectFaceWithCascades("testWithMarker.jpg")