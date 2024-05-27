
_colors = (
    # black
    b"\x00\x00\x00"
    # white
    b"\xFF\xFF\xFF"
    # red
    b"\xFF\xEB\xEE"  # 50
    b"\xFF\xCD\xD2"  # 100
    b"\xEF\x9A\x9A"  # 200
    b"\xE5\x73\x73"  # 300
    b"\xEF\x53\x50"  # 400
    b"\xF4\x43\x36"  # 500
    b"\xE5\x39\x35"  # 600
    b"\xD3\x2F\x2F"  # 700
    b"\xC6\x28\x28"  # 800
    b"\xB7\x1C\x1C"  # 900
    b"\xFF\x8A\x80"  # A100
    b"\xFF\x52\x52"  # A200
    b"\xFF\x17\x44"  # A400
    b"\xD5\x00\x00"  # A700
    # pink
    b"\xFC\xEB\xEE"  # 50
    b"\xF8\xBB\xD0"  # 100
    b"\xF4\x8F\xB1"  # 200
    b"\xF0\x62\x92"  # 300
    b"\xEC\x40\x7A"  # 400
    b"\xE9\x1E\x63"  # 500
    b"\xD8\x1B\x60"  # 600
    b"\xC2\x18\x5B"  # 700
    b"\xAD\x14\x57"  # 800
    b"\x88\x0E\x4F"  # 900
    b"\xFF\x80\xAB"  # A100
    b"\xFF\x40\x81"  # A200
    b"\xF5\x00\x57"  # A400
    b"\xC5\x11\x62"  # A700
    # purple
    b"\xF3\xE5\xF5"  # 50
    b"\xE1\xBE\xE7"  # 100
    b"\xCE\x93\xD8"  # 200
    b"\xBA\x68\xC8"  # 300
    b"\xAB\x47\xBC"  # 400
    b"\x9C\x27\xB0"  # 500
    b"\x8E\x24\xAA"  # 600
    b"\x7B\x1F\xA2"  # 700
    b"\x6A\x1B\x9A"  # 800
    b"\x4A\x14\x8C"  # 900
    b"\xEA\x80\xFC"  # A100
    b"\xE0\x40\xFB"  # A200
    b"\xD5\x00\xF9"  # A400
    b"\xAA\x00\xFF"  # A700
    # deep_purple
    b"\xED\xE7\xF6"  # 50
    b"\xD1\xC4\xE9"  # 100
    b"\xB3\x9D\xDB"  # 200
    b"\x95\x75\xCD"  # 300
    b"\x7E\x57\xC2"  # 400
    b"\x67\x3A\xB7"  # 500
    b"\x5E\x35\xB1"  # 600
    b"\x51\x2D\xA8"  # 700
    b"\x45\x27\xA0"  # 800
    b"\x31\x1B\x92"  # 900
    b"\xB3\x88\xFF"  # A100
    b"\x7C\x4D\xFF"  # A200
    b"\x65\x1F\xFF"  # A400
    b"\x62\x00\xEA"  # A700
    # indigo
    b"\xE8\xEA\xF6"  # 50
    b"\xC5\xCA\xE9"  # 100
    b"\x9F\xA8\xDA"  # 200
    b"\x79\x86\xCB"  # 300
    b"\x5C\x6B\xC0"  # 400
    b"\x3F\x51\xB5"  # 500
    b"\x39\x49\xAB"  # 600
    b"\x30\x3F\x9F"  # 700
    b"\x28\x35\x93"  # 800
    b"\x1A\x23\x7E"  # 900
    b"\x8C\x9E\xFF"  # A100
    b"\x53\x6D\xFE"  # A200
    b"\x3D\x5A\xFE"  # A400
    b"\x30\x4F\xFE"  # A700
    # blue
    b"\xE3\xF2\xFD"  # 50
    b"\xBB\xDE\xFB"  # 100
    b"\x90\xCA\xF9"  # 200
    b"\x64\xB5\xF6"  # 300
    b"\x42\xA5\xF5"  # 400
    b"\x21\x96\xF3"  # 500
    b"\x1E\x88\xE5"  # 600
    b"\x19\x76\xD2"  # 700
    b"\x15\x65\xC0"  # 800
    b"\x0D\x47\xA1"  # 900
    b"\x82\xB1\xFF"  # A100
    b"\x44\x8A\xFF"  # A200
    b"\x29\x79\xFF"  # A400
    b"\x29\x62\xFF"  # A700
    # light_blue
    b"\xE1\xF5\xFE"  # 50
    b"\xB3\xE5\xFC"  # 100
    b"\x81\xD4\xFA"  # 200
    b"\x4F\xC3\xF7"  # 300
    b"\x29\xB6\xF6"  # 400
    b"\x03\xA9\xF4"  # 500
    b"\x03\x9B\xE5"  # 600
    b"\x02\x88\xD1"  # 700
    b"\x02\x77\xBD"  # 800
    b"\x01\x57\x9B"  # 900
    b"\x80\xD8\xFF"  # A100
    b"\x40\xC4\xFF"  # A200
    b"\x00\xB0\xFF"  # A400
    b"\x00\x91\xEA"  # A700
    # cyan
    b"\xE0\xF7\xFA"  # 50
    b"\xB2\xEB\xF2"  # 100
    b"\x80\xDE\xEA"  # 200
    b"\x4D\xD0\xE1"  # 300
    b"\x26\xC6\xDA"  # 400
    b"\x00\xBC\xD4"  # 500
    b"\x00\xAC\xC1"  # 600
    b"\x00\x97\xA7"  # 700
    b"\x00\x83\x8F"  # 800
    b"\x00\x60\x64"  # 900
    b"\x84\xFF\xFF"  # A100
    b"\x18\xFF\xFF"  # A200
    b"\x00\xE5\xFF"  # A400
    b"\x00\xB8\xD4"  # A700
    # teal
    b"\xE0\xF2\xF1"  # 50
    b"\xB2\xDF\xDB"  # 100
    b"\x80\xCB\xC4"  # 200
    b"\x4D\xB6\xAC"  # 300
    b"\x26\xA6\x9A"  # 400
    b"\x00\x96\x88"  # 500
    b"\x00\x89\x7B"  # 600
    b"\x00\x79\x6B"  # 700
    b"\x00\x69\x5C"  # 800
    b"\x00\x4D\x40"  # 900
    b"\xA7\xFF\xEB"  # A100
    b"\x64\xFF\xDA"  # A200
    b"\x1D\xE9\xB6"  # A400
    b"\x00\xBF\xA5"  # A700
    # green
    b"\xE8\xF5\xE9"  # 50
    b"\xC8\xE6\xC9"  # 100
    b"\xA5\xD6\xA7"  # 200
    b"\x81\xC7\x84"  # 300
    b"\x66\xBB\x6A"  # 400
    b"\x4C\xAF\x50"  # 500
    b"\x43\xA0\x47"  # 600
    b"\x38\x8E\x3C"  # 700
    b"\x2E\x7D\x32"  # 800
    b"\x1B\x5E\x20"  # 900
    b"\xB9\xF6\xCA"  # A100
    b"\x69\xF0\xAE"  # A200
    b"\x00\xE6\x76"  # A400
    b"\x00\xC8\x53"  # A700
    # light_green
    b"\xF1\xF8\xE9"  # 50
    b"\xDC\xED\xC8"  # 100
    b"\xC5\xE1\xA5"  # 200
    b"\xAE\xD5\x81"  # 300
    b"\x9C\xCC\x65"  # 400
    b"\x8B\xC3\x4A"  # 500
    b"\x7C\xB3\x42"  # 600
    b"\x68\x9F\x38"  # 700
    b"\x55\x8B\x2F"  # 800
    b"\x33\x69\x1E"  # 900
    b"\xCC\xFF\x90"  # A100
    b"\xB2\xFF\x59"  # A200
    b"\x76\xFF\x03"  # A400
    b"\x64\xDD\x17"  # A700
    # lime
    b"\xF9\xFB\xE7"  # 50
    b"\xF0\xF4\xC3"  # 100
    b"\xE6\xEE\x9C"  # 200
    b"\xDC\xE7\x75"  # 300
    b"\xD4\xE1\x57"  # 400
    b"\xCD\xDC\x39"  # 500
    b"\xC0\xCA\x33"  # 600
    b"\xAF\xB4\x2B"  # 700
    b"\x9E\x9D\x24"  # 800
    b"\x82\x77\x17"  # 900
    b"\xF4\xFF\x81"  # A100
    b"\xEE\xFF\x41"  # A200
    b"\xC6\xFF\x00"  # A400
    b"\xAE\xEA\x00"  # A700
    # yellow
    b"\xFF\xFD\xE7"  # 50
    b"\xFF\xF9\xC4"  # 100
    b"\xFF\xF5\x9D"  # 200
    b"\xFF\xF1\x76"  # 300
    b"\xFF\xEE\x58"  # 400
    b"\xFF\xEB\x3B"  # 500
    b"\xFD\xD8\x35"  # 600
    b"\xFB\xC0\x2D"  # 700
    b"\xF9\xA8\x25"  # 800
    b"\xF5\x7F\x17"  # 900
    b"\xFF\xFF\x8D"  # A100
    b"\xFF\xFF\x00"  # A200
    b"\xFF\xEA\x00"  # A400
    b"\xFF\xD6\x00"  # A700
    # amber
    b"\xFF\xF8\xE1"  # 50
    b"\xFF\xEC\xB3"  # 100
    b"\xFF\xE0\x82"  # 200
    b"\xFF\xD5\x4F"  # 300
    b"\xFF\xCA\x28"  # 400
    b"\xFF\xC1\x07"  # 500
    b"\xFF\xB3\x00"  # 600
    b"\xFF\xA0\x00"  # 700
    b"\xFF\x8F\x00"  # 800
    b"\xFF\x6F\x00"  # 900
    b"\xFF\xE5\x7F"  # A100
    b"\xFF\xD7\x40"  # A200
    b"\xFF\xC4\x00"  # A400
    b"\xFF\xAB\x00"  # A700
    # orange
    b"\xFF\xF3\xE0"  # 50
    b"\xFF\xE0\xB2"  # 100
    b"\xFF\xCC\x80"  # 200
    b"\xFF\xB7\x4D"  # 300
    b"\xFF\xA7\x26"  # 400
    b"\xFF\x98\x00"  # 500
    b"\xFB\x8C\x00"  # 600
    b"\xF5\x7C\x00"  # 700
    b"\xEF\x6C\x00"  # 800
    b"\xE6\x51\x00"  # 900
    b"\xFF\xD1\x80"  # A100
    b"\xFF\xAB\x40"  # A200
    b"\xFF\x91\x00"  # A400
    b"\xFF\x6D\x00"  # A700
    # deep_orange
    b"\xFB\xE9\xE7"  # 50
    b"\xFF\xCC\xBC"  # 100
    b"\xFF\xAB\x91"  # 200
    b"\xFF\x8A\x65"  # 300
    b"\xFF\x70\x43"  # 400
    b"\xFF\x57\x22"  # 500
    b"\xF4\x51\x1E"  # 600
    b"\xE6\x4A\x19"  # 700
    b"\xD8\x43\x15"  # 800
    b"\xBF\x36\x0C"  # 900
    b"\xFF\x9E\x80"  # A100
    b"\xFF\x6E\x40"  # A200
    b"\xFF\x3D\x00"  # A400
    b"\xDD\x2C\x00"  # A700
    # brown
    b"\xEF\xEB\xE9"  # 50
    b"\xD7\xCC\xC8"  # 100
    b"\xBC\xAA\xA4"  # 200
    b"\xA1\x88\x7F"  # 300
    b"\x8D\x6E\x63"  # 400
    b"\x79\x55\x48"  # 500
    b"\x6D\x4C\x41"  # 600
    b"\x5D\x40\x37"  # 700
    b"\x4E\x34\x2E"  # 800
    b"\x3E\x27\x23"  # 900
    # grey
    b"\xFA\xFA\xFA"  # 50
    b"\xF5\xF5\xF5"  # 100
    b"\xEE\xEE\xEE"  # 200
    b"\xE0\xE0\xE0"  # 300
    b"\xBD\xBD\xBD"  # 400
    b"\x9E\x9E\x9E"  # 500
    b"\x75\x75\x75"  # 600
    b"\x61\x61\x61"  # 700
    b"\x42\x42\x42"  # 800
    b"\x21\x21\x21"  # 900
    # blue_grey
    b"\xEC\xEF\xF1"  # 50
    b"\xCF\xD8\xDC"  # 100
    b"\xB0\xBE\xC5"  # 200
    b"\x90\xA4\xAE"  # 300
    b"\x78\x90\x9C"  # 400
    b"\x60\x7D\x8B"  # 500
    b"\x54\x6E\x7A"  # 600
    b"\x45\x5A\x64"  # 700
    b"\x37\x47\x4F"  # 800
    b"\x26\x32\x38"  # 900
)

FAMILIES = [
    "black",
    "white",
    "red",
    "pink",
    "purple",
    "deep_purple",
    "indigo",
    "blue",
    "light_blue",
    "cyan",
    "teal",
    "green",
    "light_green",
    "lime",
    "yellow",
    "amber",
    "orange",
    "deep_orange",
    "brown",
    "grey",
    "blue_grey",
]

LENGTHS = [
    1,
    1,
    14,
    14,
    14,
    14,
    14,
    14,
    14,
    14,
    14,
    14,
    14,
    14,
    14,
    14,
    14,
    14,
    10,
    10,
    10,
]

COLORS = memoryview(_colors)
