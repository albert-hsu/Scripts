set "base_dir=%userprofile%\desktop\"
set "input_dir=%base_dir%\mpegts"
set "output_dir=%base_dir%\mp4"
for /f "delims=|" %%f in ('dir /b %input_dir%') do ffmpeg -i "%input_dir%\%%f" -acodec copy -vcodec copy "%output_dir%\%%f.mp4"
pause
