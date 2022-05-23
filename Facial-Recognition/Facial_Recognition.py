import cv2
import numpy as np
from os import listdir
from os.path import isfile, join
# 여기서부터는 Part2.py와 동일
data_path = 'faces/'
onlyfiles = [f for f in listdir(data_path) if isfile(join(data_path, f))]
Training_Data, Labels = [], []
for i, files in enumerate(onlyfiles):
    image_path = data_path + onlyfiles[i]
    images = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if images is None:
        continue
    Training_Data.append(np.asarray(images, dtype=np.uint8))
    Labels.append(i)
if len(Labels) == 0:
    print("There is no data to train.")
    exit()
Labels = np.asarray(Labels, dtype=np.int32)
model = cv2.face.LBPHFaceRecognizer_create()
model.train(np.asarray(Training_Data), np.asarray(Labels))
print("Model Training Complete!!!!!")
# 여기까지 Part2.py와 동일

# 여긴 Part1.py와 거의 동일
face_classifier = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')


def face_detector(img, size=0.5):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_classifier.detectMultiScale(gray, 1.3, 5)
    if faces is ():
        return img, []
    for(x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 255), 2)
        roi = img[y:y+h, x:x+w]
        roi = cv2.resize(roi, (200, 200))
    return img, roi  # 검출된 좌표에 사각 박스 그리고(img), 검출된 부위를 잘라(roi) 전달


# 여기까지 Part1.py와 거의 동일
# 카메라 열기
cap = cv2.VideoCapture(0)

while True:
    # 카메라로 부터 사진 한장 읽기
    ret, frame = cap.read()
    # 얼굴 검출 시도
    image, face = face_detector(frame)
    try:
        face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
        # 위에서 학습한 모델로 예측시도
        result = model.predict(face)
        # result[1]은 신뢰도이고 0에 가까울수록 자신과 같다는 뜻이다.
        if result[1] < 500:
            confidence = int(100*(1-(result[1])/300))
            display_string = str(confidence)+'% Confidence it is user'
        cv2.putText(image, display_string, (100, 120),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (250, 120, 255), 2)
        # 75 보다 클 경우 UnLocked
        if confidence > 75:
            cv2.putText(image, "Unlocked", (250, 450),
                        cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow('Face Cropper', image)
        else:
           # 75 이하일 경우 Locked
            cv2.putText(image, "Locked", (250, 450),
                        cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
            cv2.imshow('Face Cropper', image)
    except:
        # 얼굴 검출 안됨
        cv2.putText(image, "Face Not Found", (250, 450),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2)
        cv2.imshow('Face Cropper', image)
        pass
    if cv2.waitKey(1) == 13:
        break
cap.release()
cv2.destroyAllWindows()
