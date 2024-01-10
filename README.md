# Background extraction, iPhone portrait simulation Using SAM

In this free open source project, you can easily eliminate background, blur background (like portrait), and use other filters. I have used SAM (Segment Anything Model) to extract objects and for UI, I have used ttkbootstrap. It is cross-platform, therefore, you can easily use it on any OS. This is the output of application. In the left most you see original image and others are processed one.

![output](https://github.com/amirhRahimi1993/iphone_protraie/assets/39728050/7a1b38be-f421-452e-aeb0-ce3875d1f6a6)

## How to Use Method

First, you need to install requirements from `requirements.txt`. Therefore, go to the `iphone_protraie` directory and execute the command below:

```bash
cd path to iphone_protraie
pip install -r requirements.txt
```
Now you need to download .pth file from [official pytorch github](https://github.com/facebookresearch/segment-anything#model-checkpoints). I have used default one (vit_h) but you can use two other model if you want. after download the .pth checkpoint **move the .pth checkpoint to the iphone_protraie** directory. if you download vit_h model, you can run main.py.
```bash
python3 main.py
```
However, if you download other models please open main.py and change the code as below:
```python3
class Filter_image(ttk.Frame):

    def __init__(self, master):
        #Rest of the code
        self.model_name = "vit_h" # -> instead of vit_h use model name which you have downloaded from pytorch_github  [vit_l or vit_b]
        self.model_path = "sam_vit_h_4b8939.pth" #-> change the name of it
        self.SIZE= (1024, 768) -> you can change size of image if it is too big for you desktop
```
Now you can run
```bash
python3 main.py
```
If all steps execute correctly you should see something like this
![image](https://github.com/amirhRahimi1993/iphone_protraie/assets/39728050/51cda701-a3ee-402e-8bb4-8ae2c54aad8b)

ok now time for some test:
## Test the project ##
1. Click on OpenFile and choose your image
2. Click on part of image you want to segment it. **Every time you click on the object you want to segment click save point button to save it**. When you click on the image the label above the image show **(x,y)**. Click more on object make algorithm more accurate to detect object. for example I want to segment the lady in picture so I click on her face,body, toes and clothes of her.
   ![image](https://github.com/amirhRahimi1993/iphone_protraie/assets/39728050/2210d3bf-fc25-4373-9741-aeb5fcdaeb8d)

4. Now if all points are good click on **Process Image (green button)** if you want to go to step 2 first click on **Delete** and then go to step 2.
5. After click on **Process Image** if you are on cpu it take 3-4 minutes processing however if you are on gpu process take less than 1 minute
6. Now if all thing goes well you can use several filter of image
   1. For deleting background click on magnet
   2. if you want to blur the image except your segmented are click on yoga (beside magnet) button and then by scrol bar which appear right after you clicked on  yoga shaped button
   3. if you want to see other filters click on < and > buttons
  
7. What is dropdown?
   - SAM return 3 masks, 1 is the smallest mask and 3 is the largets. by default I choose 3(largest one) but you can change it.
   
8. What if I want to use other image or reset the process
   - Click on delete and upload that image or other image again!

9. if you want to save any image you like when image revealed on the app click on the floppy disk, the image automatically saved in project directory.

# Some example #

![back ground elimination](https://github.com/amirhRahimi1993/iphone_protraie/assets/39728050/e61b9ca3-f54f-4f1b-b49c-4bc34a999245)
![Bluring Image](https://github.com/amirhRahimi1993/iphone_protraie/assets/39728050/fc438182-6f2e-4e8e-85d8-fe6b34b86b51)
![One effect](https://github.com/amirhRahimi1993/iphone_protraie/assets/39728050/de476f88-5845-4e41-a154-9fde1c69c282)
![Use other mask](https://github.com/amirhRahimi1993/iphone_protraie/assets/39728050/c910bbda-4239-470d-90e2-465b71f16cd2)

# What is next?
The most important task I have to do is cleaning up the code. I have to add more classes esp in main.py





