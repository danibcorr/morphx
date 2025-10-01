# Standard libraries
import logging

# 3pps
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.generation import GenerationMixin
from transformers.modeling_utils import PreTrainedModel

# Own modules
from morphx.utils import ModelLoadError


# class for better type annotations
class _BaseModelWithGenerate(PreTrainedModel, GenerationMixin):
    pass

class SlideModel:
    """
    Esta clase permite cargar el modelo que se encarga de generar las
    Slides
    """

    model: _BaseModelWithGenerate | None = None

    def __init__(self, model_config: dict, logger: logging.Logger | None = None) -> None:
        """_summary_

        Args:
            model_id (str, optional): _description_. Defaults to "LiquidAI/LFM2-2.6B".
            logger (Optional[logging.Logger], optional): _description_. Defaults to None.
        """

        # Set attributes
        self.model_config = model_config
        self.logger = logger

    def load_model(self) -> None:
        """_summary_

        Raises:
            ModelLoadError: _description_
        """

        try:
            if torch.cuda.is_available():
                # Clear CUDA cache
                torch.cuda.empty_cache()
                self.logger.info(f"CUDA available: {torch.cuda.get_device_name(0)}")
            
            # Load tokenizer
            self.logger.debug("Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
            
            # Fix pad token issue
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                self.tokenizer.pad_token_id = self.tokenizer.eos_token_id
                self.logger.debug("Pad token configured")
            
            # Load model
            self.logger.info("Loading model...")
            self.model: _BaseModelWithGenerate = AutoModelForCausalLM.from_pretrained(
                self.model_config["slides_model"]["model_id"],
                device_map=self.model_config["slides_model"]["device_map"],
                torch_dtype=torch.bfloat16, # TODO: ADD TO CONFIGURATION
                low_cpu_mem_usage=True # TODO: ADD TO CONFIGURATION
            )   
            
            self.logger.info("Model loaded successfully.")
            
        except Exception as error:
            if self.logger:
                self.logger.error(f"Failed to load model: {str(error)}")

    def get_model(self) -> _BaseModelWithGenerate:
        """_summary_

        Raises:
            ModelLoadError: _description_

        Returns:
            _type_: _description_
        """
        
        if self.model is None:
            raise ModelLoadError("Model not loaded")

        return self.model

    