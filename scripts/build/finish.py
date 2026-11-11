"""Finishing pass shared by stills and videos: bloom + vignette on the render, then the caption on top.

Caption (ANALYSIS.md section 5): one line, 1 - 3 words, Montserrat Black, white fill, 4 px black outline,
soft 3 px shadow at 40 %, centred at x = 540, vertical centre y = 1350; a chunk replaces the previous one, no animation.

Still:  python finish.py still RENDER.png OUT.png "word"
"""
import os, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
FONTS = os.path.join(ROOT, 'assets', 'fonts')

# libass sizes are in script pixels (PlayRes = 1080 x 1920). FONT_SIZE was calibrated so that
# "a giant" measures about 263 px wide, as in the reference frame (see ANALYSIS.md, section 5).
FONT_SIZE = 100
OUTLINE = 4
SHADOW = 3

ASS_HEAD = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Montserrat Black,{FONT_SIZE},&H00FFFFFF,&H00FFFFFF,&H00000000,&H99000000,0,0,0,0,100,100,2,0,1,{OUTLINE},{SHADOW},5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def ts(t):
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f'{h}:{m:02d}:{s:05.2f}'


def write_ass(chunks, path):
    """chunks: list of (start_s, end_s, text). Consecutive chunks should touch (no gap)."""
    with open(path, 'w', encoding='utf-8') as f:
        f.write(ASS_HEAD)
        for a, b, txt in chunks:
            f.write(f'Dialogue: 0,{ts(a)},{ts(b)},Cap,,0,0,0,,{{\\an5\\pos(540,1350)}}{txt}\n')


# Glow (STYLE_NEW section 6): 0.3 above 0.75 of full brightness, blurred about 30 px, added with "screen".
# Grade: an S-curve that deepens the shadows (dark base 20 - 35 % of the frame, section 4).
# Vignette: corners about 15 % darker than the centre.
POST = ("format=gbrp,split[a][b];"
        "[b]lutrgb=r='if(gt(val,191),(val-191)*4,0)':g='if(gt(val,191),(val-191)*4,0)':b='if(gt(val,191),(val-191)*4,0)',"
        "gblur=sigma=14[g];"
        "[a][g]blend=all_mode=screen:all_opacity=0.3,"
        "curves=all='0/0 0.18/0.115 0.4/0.33 0.7/0.68 1/1',"
        "vignette=angle=0.3:mode=forward,format=yuv444p")


def still(render, out, word):
    ass = out + '.ass'
    write_ass([(0, 10, word)], ass)
    vf = POST + f",ass={ass}:fontsdir={FONTS}"
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', render, '-vf', vf, '-frames:v', '1', out], check=True)
    os.remove(ass)


if __name__ == '__main__':
    if sys.argv[1] == 'still':
        still(sys.argv[2], sys.argv[3], sys.argv[4])
