import os
import subprocess
import datetime

def get_video_framerate(video_file):
    """Gets the frame rate of a video file using ffprobe."""
    command = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=r_frame_rate",
        "-of", "default=noprint_wrappers=1:nokey=1",
        video_file
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        num, den = map(int, result.stdout.strip().split('/'))
        return num / den
    except Exception as e:
        print(f"Error getting frame rate: {e}")
        print("Please ensure ffprobe (part of FFmpeg) is installed and in your system's PATH.")
        return None

def parse_serve_frames(log_file):
    """Parses the detection log to find the first frame of each serve sequence."""
    serve_frames = []
    last_action_was_serve = False
    try:
        with open(log_file, 'r') as f:
            for line in f:
                parts = line.strip().split(',')
                if len(parts) == 2:
                    frame, action = parts
                    if action == 'serve':
                        if not last_action_was_serve:
                            serve_frames.append(int(frame))
                        last_action_was_serve = True
                    else:
                        last_action_was_serve = False
        return sorted(list(set(serve_frames))) # Return unique, sorted frames
    except FileNotFoundError:
        print(f"Error: Log file not found at '{log_file}'")
        return []

def format_time(seconds):
    """Converts seconds to HH:MM:SS.ms format for FFmpeg."""
    return str(datetime.timedelta(seconds=seconds))

def cut_rallies_with_ffmpeg(video_file, detection_log, buffer_seconds=2):
    """Finds serves and cuts the video into rallies using FFmpeg."""
    print("🚀 Starting Rally Clipper...")

    framerate = get_video_framerate(video_file)
    if not framerate:
        return

    print(f"✅ Video frame rate detected: {framerate:.2f} fps")

    serve_frames = parse_serve_frames(detection_log)
    if len(serve_frames) < 2:
        print("❗️ Not enough distinct serves found to create a rally clip. Process finished.")
        return

    print(f"✅ Found {len(serve_frames)} serves. Preparing to create {len(serve_frames) - 1} rally clips.")

    serve_times_sec = [frame / framerate for frame in serve_frames]
    output_dir = "Rally_Clips"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"\n✂️  Cutting video into rallies (outputting to '{output_dir}' folder)...")

    for i in range(len(serve_times_sec) - 1):
        start_time = max(0, serve_times_sec[i] - buffer_seconds)
        end_time = serve_times_sec[i+1] - buffer_seconds

        if end_time <= start_time:
            print(f"  -> Skipping Rally {i+1} due to overlapping times.")
            continue
            
        output_filename = os.path.join(output_dir, f"rally_{i+1}.mp4")
        
        command = [
            "ffmpeg",
            "-i", video_file,
            "-ss", str(start_time),
            "-to", str(end_time),
            "-c", "copy",
            "-y",
            output_filename
        ]
        
        print(f"  -> Creating {output_filename}...")
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    print("\n🎉 Process complete! Your rally clips are ready.")


if __name__ == '__main__':
    # Uses absolute paths, which are always correct inside the container
    FULL_GAME_VIDEO_PATH = "/app/Input/Gold_Finals_Angry_Birds_clip.mkv"
    DETECTION_LOG_PATH = "/app/Input/detection_log.txt"
    OUTPUT_DIRECTORY = "/app/Rally_Clips"

    cut_rallies_with_ffmpeg(FULL_GAME_VIDEO_PATH, DETECTION_LOG_PATH, OUTPUT_DIRECTORY)