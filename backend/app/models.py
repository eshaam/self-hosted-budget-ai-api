import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from .config import settings
import logging
import os

# Set environment variable to avoid tokenizer warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"

logger = logging.getLogger(__name__)

class QwenModel:
    def __init__(self):
        self.tokenizer = None
        self.model = None
        self.pipeline = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")
        
    def load_model(self):
        """Load the Qwen2-0.5B-Instruct model"""
        try:
            logger.info(f"Loading model: {settings.MODEL_NAME}")
            
            # Load tokenizer with explicit trust_remote_code
            self.tokenizer = AutoTokenizer.from_pretrained(
                settings.MODEL_NAME,
                cache_dir=settings.MODEL_CACHE_DIR,
                trust_remote_code=True,
                use_fast=True
            )
            
            # Ensure pad token is set
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                settings.MODEL_NAME,
                cache_dir=settings.MODEL_CACHE_DIR,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None,
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )
            
            # Move model to device if not using device_map
            if self.device == "cpu":
                self.model = self.model.to(self.device)
            
            logger.info("Model loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            return False
    
    def generate_response(self, prompt: str) -> str:
        """Generate response using the loaded model with CPU optimization"""
        try:
            logger.info(f"Starting response generation for prompt: {prompt[:50]}...")
            
            if not self.model or not self.tokenizer:
                logger.info("Model not loaded, attempting to load...")
                if not self.load_model():
                    return "Error: Model failed to load"
            
            logger.info("Model loaded successfully, generating response...")
            
            # Simple prompt format for Qwen2
            formatted_prompt = f"<|im_start|>system\nYou are a helpful AI assistant.<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"
            
            # Tokenize input with reduced max length for efficiency
            inputs = self.tokenizer(
                formatted_prompt, 
                return_tensors="pt", 
                truncation=True, 
                max_length=1024  # Reduced from 2048 for efficiency
            )
            
            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            logger.info("Starting model generation...")
            
            # CPU-optimized generation settings
            with torch.no_grad():
                # Set number of threads for CPU efficiency
                torch.set_num_threads(2)  # Limit CPU threads
                
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=min(settings.MAX_NEW_TOKENS, 30),  # Further reduced for efficiency
                    temperature=0.7,  # Fixed temperature for consistency
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    repetition_penalty=1.1,
                    num_beams=1,  # Use greedy search for efficiency
                    early_stopping=True,
                    use_cache=True  # Enable KV cache for efficiency
                )
            
            logger.info("Model generation completed, decoding response...")
            
            # Decode response
            response = self.tokenizer.decode(
                outputs[0][inputs['input_ids'].shape[1]:], 
                skip_special_tokens=True
            ).strip()
            
            logger.info(f"Response generated successfully: {response[:50]}...")
            return response if response else "I'm sorry, I couldn't generate a response."
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return f"Error generating response: {str(e)}"

# Global model instance
qwen_model = QwenModel()

def generate_response(prompt: str) -> str:
    """Public function to generate response"""
    return qwen_model.generate_response(prompt)