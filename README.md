# Text-to-Image Generator (Offline Mode)
---

This is a light-weight text-to-image generator made to run on PC's without GPU's. It uses Hugging Face's [sdxl-turbo](https://huggingface.co/stabilityai/sdxl-turbo/tree/main) AI Model to generate images based on user input. 

## **Due to how large the AI Model is, you will have to manually download it from Hugging Face's repo linked above and place it in the same folder as the python script. The script is set to look for a folder "sdxl-turbo" for the AI Model**

This was tested on a Win 11 mini PC with AMD Ryzen 5 6600H and 16GB memory. Images generated between 3-12min using between 2-15 words with an inference of 1-50.

This script allows the user to choose between 3 image sizes (256x256, 512x512, 1024,1024) and the number of inference steps from 1-50 (Lower = faster generation, Higher = slower, but better quality) and will save the images in a folder named "outputs" in the same directory as the python script.

This is an image of the GUI once you run the script.

<img width="300" height="600" alt="GUI" src="https://github.com/user-attachments/assets/4b1799aa-3fa3-4762-80f9-eaa4376fc850" />


This is how it looks when generating an image.

<img width="300" height="600" alt="GUI image generating" src="https://github.com/user-attachments/assets/bcdad6e6-20c1-4d39-9f6f-1875f24fa76b" />

This is how it looks when generated image is complete.

<img width="300" height="600" alt="GUI image complete" src="https://github.com/user-attachments/assets/97b48668-acda-4a6f-b916-c808d652edc5" />
