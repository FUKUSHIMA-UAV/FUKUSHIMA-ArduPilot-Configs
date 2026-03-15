import cv2
import numpy as np
from ultralytics import YOLO
from filterpy.kalman import KalmanFilter
from pymavlink import mavutil
import heapq

# ===== D* Lite =====
class DStarLite:
    def __init__(self, grid_size=20):
        self.size = grid_size
        self.obstacles = set()

    def heuristic(self, a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    def plan(self, start, goal):
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g = {start: 0}

        while open_set:
            _, current = heapq.heappop(open_set)
            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path

            for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
                nb = (current[0]+dx, current[1]+dy)
                if nb in self.obstacles:
                    continue
                if not (0 <= nb[0] < self.size and 0 <= nb[1] < self.size):
                    continue
                ng = g[current] + 1
                if nb not in g or ng < g[nb]:
                    g[nb] = ng
                    f = ng + self.heuristic(nb, goal)
                    heapq.heappush(open_set, (f, nb))
                    came_from[nb] = current
        return []

# ===== カルマンフィルター =====
def create_kalman(x, y):
    kf = KalmanFilter(dim_x=4, dim_z=2)
    kf.F = np.array([[1,0,1,0],[0,1,0,1],[0,0,1,0],[0,0,0,1]], dtype=float)
    kf.H = np.array([[1,0,0,0],[0,1,0,0]], dtype=float)
    kf.R *= 10
    kf.P *= 100
    kf.Q *= 0.1
    kf.x = np.array([[x],[y],[0],[0]], dtype=float)
    return kf

def pixel_to_ned(cx, cy, img_w, img_h, altitude=10):
    fov = 90
    scale = altitude * np.tan(np.radians(fov/2)) / (img_w/2)
    north = -(cy - img_h/2) * scale
    east  =  (cx - img_w/2) * scale
    return north, east

def ned_to_grid(north, east, scale=1.0, offset=10):
    gx = int(east / scale) + offset
    gy = int(-north / scale) + offset
    gx = max(0, min(19, gx))
    gy = max(0, min(19, gy))
    return (gx, gy)

# ===== MAVLink =====
master = mavutil.mavlink_connection('udp:127.0.0.1:14550')
master.wait_heartbeat()
print("機体接続完了")

# ===== YOLO =====
model = YOLO('yolo11n.pt')
img = cv2.imread('/home/userfukushima/bus.jpg')
h, w = img.shape[:2]
results = model.predict(source='/home/userfukushima/bus.jpg', show=False, classes=[0])
colors = [(255,0,0),(0,255,0),(0,0,255),(255,255,0)]

# ===== D* Lite初期化 =====
dstar = DStarLite(grid_size=20)
drone_grid = (10, 10)  # ドローンの初期位置（グリッド中心）

for i, box in enumerate(results[0].boxes):
    x1,y1,x2,y2 = map(int, box.xyxy[0])
    cx, cy = (x1+x2)//2, (y1+y2)//2
    conf = float(box.conf[0])

    kf = create_kalman(cx, cy)
    kf.predict()
    kf.update([[cx],[cy]])
    pred_x = int(kf.x[0][0])
    pred_y = int(kf.x[1][0])

    north, east = pixel_to_ned(cx, cy, w, h)
    target_grid = ned_to_grid(north, east)

    # D* Liteで経路計画
    path = dstar.plan(drone_grid, target_grid)

    color = colors[i % len(colors)]
    cv2.rectangle(img, (x1,y1), (x2,y2), color, 2)
    cv2.circle(img, (cx,cy), 5, color, -1)
    cv2.circle(img, (pred_x,pred_y), 8, (255,255,255), 2)
    cv2.putText(img, f'ID:{i+1} {conf:.2f}', (x1,y1-10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    cv2.putText(img, f'N:{north:.1f}m E:{east:.1f}m', (x1,y2+20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

    print(f'ID:{i+1} 目標グリッド:{target_grid} 経路ステップ数:{len(path)}')
    print(f'  North:{north:.1f}m East:{east:.1f}m 信頼度:{conf:.2f}')

cv2.imwrite('/home/userfukushima/dstar_output.jpg', img)
print('完了: dstar_output.jpg')
