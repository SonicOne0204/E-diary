import logging


formatter = logging.Formatter(
    fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


file_handling = logging.FileHandler("app/logging/E_diary.log")
file_handling.setFormatter(formatter)

stream_handling = logging.StreamHandler()
stream_handling.setFormatter(formatter)

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

root_logger.handlers.clear()
root_logger.addHandler(file_handling)
root_logger.addHandler(stream_handling)
