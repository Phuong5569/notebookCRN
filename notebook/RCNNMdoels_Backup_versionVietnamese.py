import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import Dense, LSTM, Reshape, BatchNormalization, Input, Conv2D, MaxPool2D, Lambda, Bidirectional, Add, Activation
from tensorflow.keras.models import Model
import tensorflow.keras.backend as K

def PreprocessData(img, resize_max_width=2167):
    """Preprocess Image
    Args:
        img (numpy.array): Image read by opencv
    Return:
        PreprocessedImage
    """
    # Convert to grayscale
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    height, width = img.shape

    # Resize to fixed height of 118, maintaining aspect ratio
    new_width = int(118 / height * width)
    img = cv2.resize(img, (new_width, 118))

    # Handle width constraint
    current_width = img.shape[1]
    if current_width > resize_max_width:
        # If image is too wide, resize it to fit max width
        img = cv2.resize(img, (resize_max_width, 118))
        current_width = resize_max_width

    # Pad to exact width of 2167 (this ensures consistent input size)
    if current_width < 2167:
        pad_width = 2167 - current_width
        img = np.pad(img, ((0, 0), (0, pad_width)), 'constant', constant_values=0)

    # Apply Gaussian blur
    img = cv2.GaussianBlur(img, (5, 5), 0)

    # Apply adaptive threshold
    img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                               cv2.THRESH_BINARY_INV, 11, 4)

    # Add channel dimension
    img = np.expand_dims(img, axis=2)

    # Normalize to [0, 1]
    img = img / 255.0

    return img


"""Create and return the OCR model architecture"""
char_list = r" #'()+,-./0123456789:ABCDEFGHIJKLMNOPQRSTUVWXYabcdeghiklmnopqrstuvwxyzÂÊÔàáâãèéêìíòóôõùúýăĐđĩũƠơưạảấầẩậắằẵặẻẽếềểễệỉịọỏốồổỗộớờởỡợụủỨứừửữựỳỵỷỹ"

# input with shape of height=118 and width=2167
inputs = Input(shape=(118,2167,1))

# Block 1
x = Conv2D(64, (3,3), padding='same')(inputs)
x = MaxPool2D(pool_size=3, strides=3)(x)
x = Activation('relu')(x)
x_1 = x

# Block 2
x = Conv2D(128, (3,3), padding='same')(x)
x = MaxPool2D(pool_size=3, strides=3)(x)
x = Activation('relu')(x)
x_2 = x

# Block 3
x = Conv2D(256, (3,3), padding='same')(x)
x = BatchNormalization()(x)
x = Activation('relu')(x)
x_3 = x

# Block4
x = Conv2D(256, (3,3), padding='same')(x)
x = BatchNormalization()(x)
x = Add()([x,x_3])
x = Activation('relu')(x)
x_4 = x

# Block5
x = Conv2D(512, (3,3), padding='same')(x)
x = BatchNormalization()(x)
x = Activation('relu')(x)
x_5 = x

# Block6
x = Conv2D(512, (3,3), padding='same')(x)
x = BatchNormalization()(x)
x = Add()([x,x_5])
x = Activation('relu')(x)

# Block7
x = Conv2D(1024, (3,3), padding='same')(x)
x = BatchNormalization()(x)
x = MaxPool2D(pool_size=(3, 1))(x)
x = Activation('relu')(x)

# pooling layer with kernel size (2,2) to make the height/2 #(1,9,512)
x = MaxPool2D(pool_size=(3, 1))(x)

# # to remove the first dimension of one: (1, 31, 512) to (31, 512)
squeezed = Lambda(lambda x: K.squeeze(x, 1))(x)

# # # bidirectional LSTM layers with units=128
blstm_1 = Bidirectional(LSTM(512, return_sequences=True, dropout = 0.2))(squeezed)
blstm_2 = Bidirectional(LSTM(512, return_sequences=True, dropout = 0.2))(blstm_1)

# # this is our softmax character proprobility with timesteps
outputs = Dense(len(char_list)+1, activation = 'softmax')(blstm_2)

def extract_text_from_image(image_path, model, char_list):
    """Extract text from a single image using the OCR model"""
    try:
        # Read and preprocess the image
        img = cv2.imread(image_path)
        if img is None:
            return ""

        processed_img = PreprocessData(img)
        # Get prediction
        processed_img = np.expand_dims(processed_img, axis=0)
        prediction = model.predict(processed_img, verbose=0)

        # Use CTC decoder
        out = K.get_value(K.ctc_decode(prediction, input_length=np.ones(prediction.shape[0])*prediction.shape[1],
                                greedy=True)[0][0])

        # Convert prediction to text
        pred_text = ""
        for p in out[0]:  # Take first (and only) prediction
            if int(p) != -1:
                pred_text += char_list[int(p)]

        if pred_text.strip() == "n":
            pred_text=""
        print(pred_text)
        return pred_text.strip()
    except Exception as e:
        print(f"Error extracting text from {image_path}: {str(e)}")
        return ""
