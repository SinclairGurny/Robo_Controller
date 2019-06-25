# video_controller.py
# Controls the video stream and computer vision
# June 2019: Sinclair Gurny

import cv2
import cv2.aruco
import face_recognition
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class VThread(QThread):
    changePixmap = pyqtSignal(QImage)
    videoReady = pyqtSignal(bool, name='vidReady')
    do_face_recog = False
    do_aruco = False
    save_face = False
    should_save_screenshot1 = False
    should_save_screenshot2 = False
    should_record_video = False
    
    def import_faces(self):
        all_names = []
        all_face_files = []
        all_encodings = []
        
        with open('Faces/Known/faces.txt', 'r') as ff:
            data = ff.readlines()
            for line in data:
                tmp = (line.rstrip()).split(' ')
                if len(tmp) != 2:
                    break
                name, face = tmp[0], tmp[1]
                all_names.append(name)
                all_face_files.append(face)
        
        for i in range(len(all_names)):
            ffile = 'Faces/Known/'+all_face_files[i]
            img = face_recognition.load_image_file(ffile)
            encod = face_recognition.face_encodings(img)[0]
            all_encodings.append(encod)

        return all_names, all_encodings
    
    def run(self):
        self.detect = True
        cap = cv2.VideoCapture()
        r = cap.open('http://192.168.1.1:8080/?action=stream')
        if not r:
            return
        else:
            self.videoReady.emit(True)

        # Video recording
        is_recording = False
        out_vid = None

        # Setup some improvements
        save_face_count = 0
        frame_count = 0
        face_locations = []
        face_encodings = []

        # Import known faces
        known_names, known_encodings = self.import_faces()
            
        # Aruco marker setup
        prev_ids = []
        tmp_file = cv2.FileStorage('robo_cam.yaml', cv2.FILE_STORAGE_READ)
        cam_mat = tmp_file.getNode('camera_matrix').mat()
        dist_mat = tmp_file.getNode('dist_coeeff').mat()
        tmp_file.release()

        while True:
            ret, frame = cap.read()
            if ret:
                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Face Recognition
                if self.do_face_recog:
                    frame_count += 1
                    if frame_count % 30 == 0:
                        face_locations = face_recognition.face_locations(rgbImage)
                        face_encodings = face_recognition.face_encodings(rgbImage, face_locations)
                        print("Faces:", face_locations)

                    for (top, right, bottom, left), face_encod in zip(face_locations, face_encodings):
                        # Check for match
                        matches = face_recognition.compare_faces(known_encodings, face_encod)

                        name = 'Unknown'
                        if True in matches:
                            first_match_index = matches.index(True)
                            name = known_names[first_match_index]

                        # Draw box
                        cv2.rectangle(rgbImage, (left, top), (right, bottom), (255,0,0), 1)
                        # Label name
                        cv2.rectangle(rgbImage, (left, bottom), (right, bottom+20), (255,0,0), cv2.FILLED)
                        font = cv2.FONT_HERSHEY_SIMPLEX
                        cv2.putText(rgbImage, name, (left + 2, bottom + 13), font, 0.5, (255,255,255), 1)

                    if self.save_face:
                        print("Saving face")
                        for top, right, bottom, left in face_locations:
                            face_img = frame[top:bottom, left:right]
                            img_file = 'Faces/Unknown/face'+str(save_face_count)+'.png'
                            cv2.imwrite(img_file, face_img)
                            save_face_count += 1
                # ==============================================================

                # Recording
                if self.should_save_screenshot1:
                    print("Save screenshot 1!")
                    timestamp = datetime.now().strftime('%d%b_%H:%M:%S')
                    screenshot_name = 'Screenshots/pic_'+timestamp+'.png'
                    new_frame = frame.copy()
                    cv2.imwrite(screenshot_name, new_frame)
                    
                if self.should_save_screenshot2:
                    print("Save screenshot 2!")
                    timestamp = datetime.now().strftime('%d%b_%H:%M:%S')
                    screenshot_name = 'Screenshots/pic_'+timestamp+'.png'
                    new_frame = rgbImage.copy()
                    cv2.imwrite(screenshot_name, new_frame)

                if is_recording:
                    if self.should_record_video:
                        # save next frame
                        out_vid.write(frame)
                    else:
                        # stop and save
                        print("Done Recording")
                        out_vid.release()
                        is_recording = False
                else:
                    if self.should_record_video:
                        # start recording
                        print("Starting Recoding!")
                        timestamp = datetime.now().strftime('%d%b_%H:%M:%S')
                        video_name = 'Videos/vid_'+timestamp+'.avi'
                        v_width = int(cap.get(3))
                        v_height = int(cap.get(4))
                        out_vid = cv2.VideoWriter(video_name, cv2.VideoWriter_fourcc('M','J','P','G'), \
                                        20, (v_width, v_height))
                        is_recording = True

                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQtFormat = QImage(rgbImage, w, h, bytesPerLine,\
                                           QImage.Format_RGB888)
                p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
                self.changePixmap.emit(p)
