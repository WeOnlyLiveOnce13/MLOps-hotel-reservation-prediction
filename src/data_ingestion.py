import os
import pandas as pd
from google.cloud import storage
from sklearn.model_selection import train_test_split
from src.logger import get_logger
from src.custom_exception import CustomException
from config.paths_config import *
from utils.common_functions import read_yaml

logger = get_logger(__name__)

class DataIngestion:
    def __init__(self,config):
        self.config = config["data_ingestion"]
        self.bucket_name = self.config["bucket_name"]
        self.file_name = self.config["bucket_file_name"]
        self.train_test_ratio = self.config["train_ratio"]

        os.makedirs(RAW_DIR , exist_ok=True)

        logger.info(f"Data Ingestion started with {self.bucket_name} and file is  {self.file_name}")

    # def download_csv_from_gcp(self):
    #     try:
    #         client = storage.Client()
    #         bucket = client.bucket(self.bucket_name)
    #         blob = bucket.blob(self.file_name)

    #         blob.download_to_filename(RAW_FILE_PATH)

    #         logger.info(f"CSV file is successfully downloaded to {RAW_FILE_PATH}")

    #     except Exception as e:
    #         logger.error("Error while downloading the csv file")
    #         raise CustomException("Failed to downlaod csv file ", e)
        

    def download_csv_from_gcp(self):
        try:
            logger.info(f"Attempting to download file '{self.file_name}' from bucket '{self.bucket_name}'")
            
            # Check if credentials are properly set up
            if not os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'):
                logger.warning("GOOGLE_APPLICATION_CREDENTIALS environment variable not set")
            
            client = storage.Client()
            logger.info("Successfully created GCP storage client")
            
            # Verify bucket exists
            try:
                bucket = client.bucket(self.bucket_name)
                if not bucket.exists():
                    logger.error(f"Bucket '{self.bucket_name}' does not exist")
                    raise CustomException(f"Bucket '{self.bucket_name}' does not exist", None)
                logger.info(f"Successfully accessed bucket '{self.bucket_name}'")
            except Exception as e:
                logger.error(f"Error accessing bucket '{self.bucket_name}': {str(e)}")
                raise CustomException(f"Failed to access bucket '{self.bucket_name}'", e)
            
            # Verify blob exists
            blob = bucket.blob(self.file_name)
            try:
                if not blob.exists():
                    logger.error(f"File '{self.file_name}' does not exist in bucket '{self.bucket_name}'")
                    raise CustomException(f"File '{self.file_name}' not found in bucket", None)
                logger.info(f"File '{self.file_name}' found in bucket")
            except Exception as e:
                logger.error(f"Error checking if file '{self.file_name}' exists: {str(e)}")
                raise CustomException(f"Failed to verify file existence", e)
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(RAW_FILE_PATH), exist_ok=True)
            
            # Attempt download
            logger.info(f"Starting download to {RAW_FILE_PATH}")
            blob.download_to_filename(RAW_FILE_PATH)
            
            # Verify file was downloaded
            if os.path.exists(RAW_FILE_PATH):
                file_size = os.path.getsize(RAW_FILE_PATH)
                logger.info(f"CSV file successfully downloaded to {RAW_FILE_PATH} (size: {file_size} bytes)")
            else:
                logger.error(f"Download completed but file not found at {RAW_FILE_PATH}")
                raise CustomException("File download failed - file not created", None)

        except Exception as e:
            logger.error(f"Error while downloading the CSV file: {str(e)}")
            raise CustomException("Failed to download CSV file", e)
        
    def split_data(self):
        try:
            logger.info("Starting the splitting process")
            data = pd.read_csv(RAW_FILE_PATH)
            train_data , test_data = train_test_split(data , test_size=1-self.train_test_ratio , random_state=42)

            train_data.to_csv(TRAIN_FILE_PATH)
            test_data.to_csv(TEST_FILE_PATH)

            logger.info(f"Train data saved to {TRAIN_FILE_PATH}")
            logger.info(f"Test data saved to {TEST_FILE_PATH}")
        
        except Exception as e:
            logger.error("Error while splitting data")
            raise CustomException("Failed to split data into training and test sets ", e)
        
    def run(self):

        try:
            logger.info("Starting data ingestion process")

            self.download_csv_from_gcp()
            self.split_data()

            logger.info("Data ingestion completed successfully")
        
        except CustomException as ce:
            logger.error(f"CustomException : {str(ce)}")
        
        finally:
            logger.info("Data ingestion completed")

if __name__ == "__main__":
    data_ingestion = DataIngestion(read_yaml(CONFIG_PATH))
    data_ingestion.run()




        

