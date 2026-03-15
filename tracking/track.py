import cv2
import numpy as np
from ultralytics import YOLO
from filterpy.kalman import KalmanFilter

def create_kalman(x, y):
    kf = KalmanFilter(dim_x=4, dim_z=2)
    kf.F = np.array([[1,0,1,0],[0,1,0,1],[0,0,1,0],[0,0,0,1]], dtype=float)
    kf.H = np.array([[1,0,0,0],[0,1,0,0]], dtype=float)
    kf.R *= 10
    kf.P *= 100
    kf.Q *= 0.1
    kf.x = np.array([[x],[y],[0],[0]], dtype=float)
    return kf

model = YOLO('yolo11n.pt')
img = cv2.imread('/home/userfukushima/bus.jpg')
results = model.predict(source='/home/userfukushima/bus.jpg', show=False, classes=[0])

colors = [(255,0,0),(0,255,0),(0,0,255),(255,255,0)]

for i, box in enumerate(results[0].boxes):
    x1,y1,x2,y2 = map(int, box.xyxy[0])
    cx, cy = (x1+x2)//2, (y1+y2)//2
    conf = float(box.conf[0])
    kf = create_kalman(cx, cy)
    kf.predict()
    kf.update([[cx],[cy]])
    pred_x = int(kf.x[0][0])
    pred_y = int(kf.x[1][0])
    color = colors[i % len(colors)]
    cv2.rectangle(img, (x1,y1), (x2,y2), color, 2)
    cv2.circle(img, (cx,cy), 5, color, -1)
    cv2.circle(img, (pred_x,pred_y), 8, (255,255,255), 2)
    cv2.putText(img, f'ID:{i+1} {conf:.2f}', (x1,y1-10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

cv2.imwrite('/home/userfukushima/tracked_output.jpg', img)
print('保存完了')
print(f'検出人数: {len(results[0].boxes)}人')
