# Scenery
This is a website I built to play a bunch of videos I recorded in a loop. It uses Resend to send verification emails, and integrates with Stripe to support a subscription feature. 
You can test my version at [scenery.aurorii.com](https://scenery.aurorii.com).

# Getting Started
You can simply clone the repo, and then run `setup.py` which will install required dependencies, and help you configure your environment variables. If you want to use a virtual environment, make sure to set that up before running the script.
The setup script will ask you for your database's URI, so have that handy. I tested with Postgres.
Finally, run `main.py`.

## Features
- Mail system
- Dashboard with Analytics
- Integration with Stripe
- Mobile + Desktop compatibility
- Upload + Process videos via FFMPEG

## Todo List
- Allow selection of audience for mailing lists.
- Properly spinoff FFMPEG process so it doesn't crash Gunicorn worker.
- Investifate bug where logging in fails with email not found error, but succeeds on second attempt.

# Screenshots
<img width="2876" height="1537" alt="Screenshot From 2026-01-02 21-19-39" src="https://github.com/user-attachments/assets/5e968700-7d9e-4582-aaa1-de44e99c7817" />
<img width="2876" height="1537" alt="Screenshot From 2026-01-02 21-20-12" src="https://github.com/user-attachments/assets/ffade635-b227-49e5-b096-e98cbfbf8ab5" />
<img width="2876" height="1537" alt="Screenshot From 2026-01-02 21-20-31" src="https://github.com/user-attachments/assets/0a2ff49e-b87a-464e-bc5e-7be03590bf60" />
