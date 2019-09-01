"""
This is responsible for analyzing a single video file and marking logical/virtual
chunks that builds up the actual video file. The basic idea is to mark sections of
the original video such that it can be analyzed as parts/chunks, without
actually breaking the video into pieces/separate files.
"""
import cv2
import os
import math

def frame_count(video_path: str) -> int:
    """
    Counts the total number of frames in a given video file.

    :param video_path
        Absolute path to the video file.
        (Relative path should also work but stick to absolute).
    
    :returns int
        Number of frames.
        -1  ->  File not found.
        0   ->  File is not a video | File has no frames.
        >0  ->  Number of frames.
    """

    if os.path.isfile(video_path):
        cap = cv2.VideoCapture(video_path)
        property_id = int(cv2.CAP_PROP_FRAME_COUNT) 
        length = int(cv2.VideoCapture.get(cap, property_id))
        return length
    else:
        print('File at {filepath} could not be found.'.format(filepath=video_path))
        return -1

def duration(video_path: str) -> float:
    """
    Finds the length of the video in miliseconds.

    :param video_path
        Absolute path to the video file.
        (Relative path should also work but stick to absolute).
    
    :returns float
        Total time/duration.
        -1  ->  File not found.
        0   ->  File is not a video | File has duration.
        >0  ->  Video length in miliseconds.
    """

    if os.path.isfile(video_path):
        cap = cv2.VideoCapture(video_path)
        cap.set(cv2.CAP_PROP_POS_AVI_RATIO,1)
        duration = cap.get(cv2.CAP_PROP_POS_MSEC)
        return duration
    else:
        print('File at {filepath} could not be found.'.format(filepath=video_path))
        return -1


def video_metadata(video_path: str) -> dict:
    """
    Returns metadata of a video such as
        Frame count
        Duration in miliseconds
        FPS
    along with the measuring unit.

    Ex: 
    {
        'Frames': { 'Value': 1000, 'Unit': 'sum' },
        'Duration': { 'Value': 60, 'Unit': 'seconds' },
        'FPS': { 'Value': 16, 'Unit': 'fps' },
    }

    :param video_path
        Absolute path to the video file.
        (Relative path should also work but stick to absolute).
    
    :returns dict
        Contains above 3 aspects in a single dict object.
    """

    frames = frame_count(video_path)
    time = duration(video_path) / (1000)   # in seconds.
    frame_rate = int(frames/time) if not (time or frames) <= 0 else 0  # frames per second | fps.

    return {
        'Frames': { 'Value': frames, 'Unit': 'sum' },
        'Duration': { 'Value': time, 'Unit': 'second' },
        'FPS': { 'Value': frame_rate, 'Unit': 'fps' },
    }


def get_logical_chunks(video_path: str, chunk_length=60) -> list:
    """
    Creates a list of logical video chunks by analyzing the given single video file.
    NOTE: Each video chunk is 1 minute long.

    Start and end point of each chunk is defined as the frame number to start reading,
    and the frame number of stop reading at.
    NOTE: Frame rate affects this.
    
    :param video_path
        Absolute path to the video file.
        (Relative path should also work but stick to absolute).
    :param chunk_length
        Length of a logical video chunk in seconds.
        OPTIONAL
        DEFAULT = 60

    :returns list
        A list of dictionaries where each dictionary specifies a starting and ending point
        on the original video file.
    """

    metadata = video_metadata(video_path)
    frame_count, duration, fps = metadata['Frames']['Value'], metadata['Duration']['Value'], metadata['FPS']['Value']

    if (frame_count and duration and fps) > 0:
        frame_count_per_chunk = fps * chunk_length
        chunks = []
        chunk_number = 1
        chunk_total = math.ceil(frame_count / frame_count_per_chunk)

        for i in range(1, frame_count, frame_count_per_chunk):
            start_frame = i
            end_frame = i + frame_count_per_chunk
            # Normalize end_frame.
            end_frame = frame_count if end_frame > frame_count else end_frame

            chunks.append({
                'ParentMooc': video_path.split('+')[0]  if '+' in video_path else 'InvalidNaming',
                'ParentFile': video_path.split('/').pop(),  # Just get the file name.
                'StartFrame': start_frame,
                'EndFrame': end_frame,
                'Position': chunk_number,
                'Total': chunk_total
            })

            chunk_number += 1
        
        return chunks
    else:
        return []

