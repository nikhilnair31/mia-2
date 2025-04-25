import os
import re
import json
import time
import boto3
import base64
import logging
import datetime
import traceback
from db import (
    initialize_screenshots_tbl, 
    insert_to_screenshots_tbl
)
from file import (
    check_s3_object_exists, 
    get_s3_file_metadata, 
    file_download, file_upload
)
from image import (
    preprocess_image
)
from llm import (
    call_llm_api
)

logger = logging.getLogger()
logger.setLevel("INFO")

s3 = boto3.client('s3')

BUCKET_NAME = 'mia-2'
IMAGE_TEMP_FILEPATH = f"/tmp/temp_image_file.mp3"
DB_TEMP_FILEPATH = f"/tmp/screenshots.db"
PATTERN = rf'<tags>(.*?)<\/tags>'

def start_process(image_objectkey, image_filepath, db_filepath):
    PROCESS_SYSTEM_PROMPT = """
        You are an advanced computer vision model specialized in analyzing screenshots from Android phones, particularly those of social media apps. Your task is to extract relevant and descriptive tags or keywords from the input image, focusing on UI elements, app features, content types, and other notable elements that can be used for similarity-based searching.

        Here is the input image for analysis:

        <input_image>
        {{INPUT_IMAGE}}
        </input_image>

        Please follow these steps to analyze the image and generate tags:

        1. Carefully examine the image content, paying close attention to:
        - User interface elements (e.g., buttons, menus, navigation bars)
        - App features (e.g., messaging, posts, stories, reactions)
        - Content types (e.g., text, images, videos)
        - Themes or color schemes (be specific about colors and styles)
        - Any text visible in the image
        - Identifiable logos or app names
        - Overall layout and design
        - User interactions or activities represented
        - Unique or distinguishing characteristics

        2. Based on your observations, estimate the most likely app or platform represented in the screenshot. Consider layouts, potential user accounts, and other identifying features.

        3. Provide a detailed analysis of your observations inside <image_breakdown> tags. Include:
        - A numbered list of prominent UI elements, describing their appearance and function. Count these out loud (e.g., "1. Profile picture, 2. Menu button, 3. Search bar").
        - A numbered list of visible app features, explaining how they are represented. Count these out loud as well.
        - A numbered list of content types present, including any specific details about the content.
        - A detailed color analysis, listing out specific colors you observe (e.g., "1. Navy blue (#000080), 2. Crimson red (#DC143C)").
        - Quotes of any visible text or logos
        - Your estimated app or platform identification with reasoning
        - A numbered list of potential user interactions or activities represented
        - Any unique or distinguishing characteristics, focusing on specific design elements, animations, or interactive features

        4. Based on your analysis, brainstorm a list of potential tags or keywords inside <potential_tags> tags. These should be concise, descriptive, and useful for searching similar images. Include specific color names, design elements, and unique features.

        5. From your brainstormed list, select and refine the most relevant tags. Format your final output as a comma-separated list of tags, ensuring that:
        - Each tag is a single word or a short phrase (2-3 words maximum)
        - Tags are ordered from most to least relevant
        - There are no duplicates
        - The list contains at least 5 tags but no more than 15
        - The estimated app name or platform is included as a tag
        - Specific colors, themes, and distinctive design elements are included

        6. Present your final list of tags using <tags> tags.

        Example output format:

        <image_breakdown>
        UI Elements:
        1. Rounded profile picture in top-left corner, 40x40 pixels, surrounded by a 2px blue border
        2. "Post" button in top-right corner, light blue text on white background
        3. Bottom navigation bar with 5 icons

        App Features:
        1. Story carousel at the top, horizontal scrolling with circular thumbnails
        2. Like button represented by a heart icon, changes color when tapped
        3. Comment section below each post

        Content Types:
        1. Square images in a 3-column grid layout, each approximately 120x120 pixels
        2. Short video clips indicated by a play button overlay
        3. Text captions below each post

        Color Analysis:
        1. White (#FFFFFF) - Predominant background color
        2. Light Blue (#3897F0) - Accent color for buttons and icons
        3. Dark Blue (#1E3040) - Text color
        4. Gray (#8E8E8E) - Secondary text and icon color

        Visible Text/Logos: "Instagram" logo in customized script font at top center

        Estimated App/Platform: Instagram - Reasoning: Distinctive grid layout, story carousel, and recognizable logo

        User Interactions/Activities:
        1. Double-tap to like posts
        2. Horizontal swipe to view stories
        3. Tap on profile picture to view user profile
        4. Scroll vertically to browse feed

        Unique Characteristics: Custom heart animation when liking a post, gradient effect on story thumbnails
        </image_breakdown>

        <potential_tags>
        instagram, social_media, photo_sharing, story_carousel, grid_layout, profile_picture, post_button, like_heart, blue_accent, white_background, custom_animation, gradient_effect, square_images, horizontal_scroll, double_tap_interaction, video_content, comment_section, navigation_bar
        </potential_tags>

        <tags>
        instagram, social_media, blue_accent, white_background, gradient_effect, square_images, horizontal_scroll, video_content
        </tags>

        Please provide your analysis, tag brainstorming, and then the final list of tags for the given input image.
    """
    
    # Read image file and convert to base64
    with open(image_filepath, "rb") as image_file:
        image_bytes = image_file.read()
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")
    
    db_success = initialize_screenshots_tbl(db_filepath)
    if not db_success:
        raise Exception(f"Failed to initialize table SCREENSHOTS at {db_filepath}")
    
    response = call_llm_api(PROCESS_SYSTEM_PROMPT, image_b64)
    analysis_raw_json_str = json.dumps(response)
    # logger.info(f'response: {response}')
    analysis_raw_text = response['candidates'][0]['content']['parts'][0]['text']
    matches = re.findall(PATTERN, analysis_raw_text, re.DOTALL)
    if matches:
        analysis_raw_text = matches[0].strip().split(', ')
        analysis_raw_text = ','.join(analysis_raw_text)
    logger.info(f'analysis_raw_text: {analysis_raw_text}')
    if not analysis_raw_text:
        raise Exception("LLM call failed")
    
    timestamp_str = str(datetime.datetime.now())
    # logger.info(f"timestamp_str: {timestamp_str}")
    
    insert_data = (
        image_objectkey,
        analysis_raw_json_str,
        analysis_raw_text,
        timestamp_str
    )
    # logger.info(f"insert_data: {insert_data}")
    insert_success = insert_to_screenshots_tbl(db_filepath, insert_data)
    if not insert_success:
        raise Exception("Failed to insert to table SCREENSHOTS")
    
    logger.info("Process completed successfully")
    return True

def lambda_handler(event, context):
    logger.info(f"Event: {event}")
    
    try:
        # Get event details
        record = event['Records'][0]
        image_object_key = record['s3']['object']['key']
        logger.info(f"image_object_key: {image_object_key}")

        # Get image file metadata
        image_metadata = get_s3_file_metadata(s3, BUCKET_NAME, image_object_key)
        logger.info(f"image_metadata: {image_metadata}")

        # Download image file from S3
        image_download_success = file_download(s3, BUCKET_NAME, image_object_key, IMAGE_TEMP_FILEPATH)
        if not image_download_success:
            raise Exception(f"Failed to download image file from S3: {BUCKET_NAME}/{image_object_key}")

        # Check by metadata if can be processed
        processed_image_temp_filepath = IMAGE_TEMP_FILEPATH
        if image_metadata.get('preprocessfile') == 'true':
            processed_image_temp_filepath = preprocess_image(IMAGE_TEMP_FILEPATH)
        
        # Download db file from S3
        user_name = image_object_key.split('/')[1] if '/' in image_object_key else ''
        db_object_key = f'data/{user_name}/user_data.db'
        db_exists = check_s3_object_exists(s3, BUCKET_NAME, db_object_key)
        if db_exists:
            db_download_success = file_download(s3, BUCKET_NAME, db_object_key, DB_TEMP_FILEPATH)
            if not db_download_success:
                raise Exception(f"Failed to download database file from S3: {BUCKET_NAME}/{db_object_key}")
        else:
            db_init_success = initialize_screenshots_tbl(DB_TEMP_FILEPATH)
            if not db_init_success:
                raise Exception(f"Failed to initialize new database at {DB_TEMP_FILEPATH}")
        
        # Process image
        save_image_object_key = image_object_key if image_metadata.get('savefile') == 'true' else '-'
        start_process(save_image_object_key, processed_image_temp_filepath, DB_TEMP_FILEPATH)
        
        # Upload db to S3
        db_upload_success = file_upload(s3, BUCKET_NAME, db_object_key, DB_TEMP_FILEPATH)
        if not db_upload_success:
            raise Exception(f"Failed to upload database file from S3: {BUCKET_NAME}/{db_object_key}")
        
        # Delete image in s3
        if image_metadata.get('savefile') == 'false':
            image_delete_success = s3.delete_object(Bucket=BUCKET_NAME, Key=image_object_key)
            if not image_delete_success:
                raise Exception(f"Failed to delete image file from S3: {BUCKET_NAME}/{image_object_key}")
        
        return {
            "statusCode": 200, 
            "body": "Process completed successfully"
        }
        
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(f"Error in lambda_handler: {str(e)}\nStacktrace:\n{error_traceback}")
        return {
            "statusCode": 500,
            "body": f"Error: {str(e)}\nStacktrace:\n{error_traceback}"
        }