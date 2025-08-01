# Text-to-Image Generator (Offline Mode)
---

This is a light-weight text-to-image generator made to run on PC's without GPU's. It uses Hugging Face's [sdxl-turbo](https://huggingface.co/stabilityai/sdxl-turbo/tree/main) AI Model to generate images based on user input.

## **Due to how large the AI Model is, you will have to manually download it from Hugging Face's repo linked above and place it in the same folder as the python script. The script is set to look for a folder "sdxl-turbo" for the AI Model**

This was tested on a Win 11 mini PC with AMD Ryzen 5 6600H and 16GB memory. Images generated between 3-12min using between 2-15 words with an inference of 1-50.
