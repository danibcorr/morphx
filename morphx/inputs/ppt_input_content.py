PPT_INPUT_CONTENT: str = """
    ### Slide 1

    Identifier: `SL1`
    Main Title: Introduction to Deep Learning
    Subtitle: Fundamental concepts of intelligence and artificial intelligence

    Key Points and Description:

    1. Intelligence

    + Defined as the ability to process information and use it to make future decisions.
    + Intelligence involves analyzing data, anticipating outcomes, and adapting behavior to different contexts.

    2. Artificial Intelligence (AI)

    + A field focused on developing techniques and algorithms that allow machines to emulate certain human behaviors.
    + AI systems use available information to predict outcomes, adapt to changing contexts, and solve problems autonomously.

    3. Machine Learning (ML)

    + A subfield of AI that enables computers to learn from experience without explicit instructions.
    + ML algorithms identify patterns in data and improve performance automatically, replacing traditional step-by-step programming.

    4. Deep Learning (DL)

    + A specialized branch of ML based on artificial neural networks that extract complex patterns from raw data.
    + DL learns hierarchical representations, enabling the system to understand complex relationships and perform tasks such as image recognition, natural language processing, and audio analysis.

    ---

    ### Slide 2

    Identifier: `SL2`
    Main Title: Introduction to Deep Learning
    Subtitle: Predicting house prices using linear regression

    Key Points and Description:

    1. Linear Regression

    + A basic mathematical model that fits a line to data to capture relationships between variables.
    + Example: predicting house prices based on size. Larger houses tend to have higher prices, but linear models may produce invalid predictions for extreme values.

    2. Neuron or Perceptron

    + Functions as a computational unit that receives input, performs a weighted calculation, and applies a function to produce a coherent output.
    + Extends simple regression to multiple inputs (e.g., bedrooms, location) for more accurate predictions.

    3. Layered Architectures

    + Combining multiple linear models in layers creates more complex structures capable of handling high-dimensional data.
    + Consists of input layers (receiving initial features), hidden layers (transforming and combining features), and output layers (producing final predictions).

    ---

    ### Slide 3

    Identifier: `SL3`
    Main Title: Introduction to Deep Learning
    Subtitle: Essential components of an artificial neuron

    Key Points and Description:

    1. Weights

    + Each input feature is assigned a weight reflecting its relative importance.
    + Weights adjust during training to optimize model performance.

    2. Bias

    + A value added to the neuron's calculation to increase flexibility.
    + Allows the neuron to adjust its output independently of the input, enhancing the model’s adaptability.

    3. Activation Function

    + A non-linear function applied to the neuron’s output.
    + Enables the network to capture complex relationships beyond linear combinations and ensures outputs remain within a meaningful range.

    4. Training Process

    + Involves adjusting weights and biases to minimize prediction error.
    + Optimizes the network to accurately generalize from examples to new data.

    ---

    ### Slide 4

    Identifier: `SL4`
    Main Title: Introduction to Deep Learning
    Subtitle: Types of architectures and data

    Key Points and Description:

    1. Neural Network Architectures

    + Dense (fully connected) networks: suited for tabular data.
    + Convolutional Neural Networks (CNNs): designed to analyze images and videos through spatial pattern detection.
    + Recurrent Neural Networks (RNNs) and variants: effective for sequential data such as text, audio, and time series.
    + Multimodal models: integrate information from multiple sources, including text, images, and sound.

    2. Data Types

    + Structured data: organized in rows and columns; traditional ML algorithms often suffice.
    + Unstructured data: includes images, audio, and free-text documents; DL excels at extracting complex patterns from large volumes of unstructured information.

    ---

    ### Slide 5

    Identifier: `SL5`
    Main Title: Introduction to Deep Learning
    Subtitle: Factors driving the development of Deep Learning

    Key Points and Description:

    1. Massive Data Availability

    + Digitalization and global connectivity generate large datasets required to train complex models.

    2. Advances in Specialized Hardware

    + GPUs and TPUs accelerate training of large-scale models.
    + Hardware innovations, including NPUs, allow efficient, private, and offline AI execution on mobile and embedded devices.

    3. Improvements in Algorithms and Optimization Techniques

    + Enable the solution of previously intractable problems.
    + Combined with open-source models and datasets, these advances democratize access to DL, fostering research and innovation in AI applications.
"""
