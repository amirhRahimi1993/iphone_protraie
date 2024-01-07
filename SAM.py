import copy
import sys
import cv2
import numpy as np
import matplotlib.pyplot as plt
sys.path.append("..")
from segment_anything import sam_model_registry, SamPredictor


class SAM:
    def __init__(self,img_path: str,model_name:str, model_path:str,device:str):
        self.results = {}
        self.image = cv2.imread(img_path)
        self.gray_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        self.rgb_image = copy.deepcopy(cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB))
        self.image = copy.deepcopy(self.rgb_image)

        self.__apply_sobel()

        self.__change_all_img_to_rgb()
        self.sam_checkpoint = model_path
        self.model_type = model_name

        self.device = device

    def __apply_sobel(self):
        ksize = 3
        gX = cv2.Sobel(self.gray_image, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=ksize)
        gY = cv2.Sobel(self.gray_image, ddepth=cv2.CV_32F, dx=0, dy=1, ksize=ksize)

        gX = cv2.convertScaleAbs(gX)
        gY = cv2.convertScaleAbs(gY)
        self.sobel_edge = cv2.addWeighted(gX, 0.5, gY, 0.5, 0)
    def __change_all_img_to_rgb(self):
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        self.sobel_edge = cv2.cvtColor(self.sobel_edge, cv2.COLOR_GRAY2RGB)
        self.gray_image = cv2.cvtColor(self.gray_image, cv2.COLOR_GRAY2RGB)

    def __show_mask(self,mask, ax, random_color=False):
        if random_color:
            color = np.concatenate([np.random.random(3), np.array([0.6])], axis=0)
        else:
            color = np.array([30 / 255, 144 / 255, 255 / 255, 0.6])
        h, w = mask.shape[-2:]
        mask_image = mask.reshape(h, w, 1) * color.reshape(1, 1, -1)
        ax.imshow(mask_image)


    def __show_points(self,coords, labels, ax, marker_size=375):
        pos_points = coords[labels == 1]
        neg_points = coords[labels == 0]
        ax.scatter(pos_points[:, 0], pos_points[:, 1], color='green', marker='*', s=marker_size, edgecolor='white',
                   linewidth=1.25)
        ax.scatter(neg_points[:, 0], neg_points[:, 1], color='red', marker='*', s=marker_size, edgecolor='white',
                   linewidth=1.25)


    def __show_box(self,box, ax):
        x0, y0 = box[0], box[1]
        w, h = box[2] - box[0], box[3] - box[1]
        ax.add_patch(plt.Rectangle((x0, y0), w, h, edgecolor='green', facecolor=(0, 0, 0, 0), lw=2))


    def process_data(self,input_point):
        sam = sam_model_registry[self.model_type](checkpoint=self.sam_checkpoint)
        sam.to(device=self.device)

        predictor = SamPredictor(sam)


        predictor.set_image(self.image)

        input_label = np.array([i for i in range(1,len(input_point)+1)])


        masks, scores, logits = predictor.predict(
            point_coords=np.asarray(input_point),
            point_labels=input_label,
            multimask_output=True,
        )

        rgb_gray_binary= {"rbg":self.rgb_image,"gray":self.gray_image,"sobel":self.sobel_edge,"empty":np.zeros(self.image.shape),"mask":masks}
        return rgb_gray_binary

    def __save_mask(self,masks,scores,input_point,input_label):
        for i, (mask, score) in enumerate(zip(masks, scores)):
            plt.figure(figsize=(10,10))
            plt.imshow(self.image)
            self.__show_mask(mask, plt.gca())
            self.__show_points(input_point, input_label, plt.gca())
            plt.title(f"Mask {i+1}, Score: {score:.3f}", fontsize=18)
            plt.axis('off')
            plt.show()