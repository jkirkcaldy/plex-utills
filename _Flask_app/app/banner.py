import cv2, imagehash
from PIL import Image

banner_4k = cv2.imread("app/img/4K-Template.png", cv2.IMREAD_UNCHANGED)
banner_4k = Image.fromarray(banner_4k)
mini_4k_banner = cv2.imread("app/img/4K-mini-Template.png", cv2.IMREAD_UNCHANGED)
mini_4k_banner = Image.fromarray(mini_4k_banner)
banner_dv = cv2.imread("app/img/dolby_vision.png", cv2.IMREAD_UNCHANGED)
banner_dv = Image.fromarray(banner_dv)
banner_hdr10 = cv2.imread("app/img/hdr10.png", cv2.IMREAD_UNCHANGED)
banner_hdr10 = cv2.cvtColor(banner_hdr10, cv2.COLOR_BGR2RGBA)
banner_hdr10 = Image.fromarray(banner_hdr10)

banner_new_hdr = cv2.imread("app/img/hdr.png", cv2.IMREAD_UNCHANGED)
banner_new_hdr = Image.fromarray(banner_new_hdr)
atmos = cv2.imread("app/img/atmos.png", cv2.IMREAD_UNCHANGED)
atmos = Image.fromarray(atmos)
dtsx = cv2.imread("app/img/dtsx.png", cv2.IMREAD_UNCHANGED)  
dtsx = Image.fromarray(dtsx)



# General Hashes
chk_banner = Image.open("app/img/chk-4k.png")
chk_banner_hash = imagehash.average_hash(chk_banner)
chk_mini_banner = Image.open("app/img/chk-mini-4k2.png")
chk_mini_banner_hash = imagehash.average_hash(chk_mini_banner)
chk_hdr = Image.open("app/img/chk_hdr.png")
chk_hdr_hash = imagehash.average_hash(chk_hdr)
chk_dolby_vision = Image.open("app/img/chk_dolby_vision.png")
chk_dolby_vision_hash = imagehash.average_hash  (chk_dolby_vision)
chk_hdr10 = Image.open("app/img/chk_hdr10.png")
chk_hdr10_hash = imagehash.average_hash(chk_hdr10)
chk_new_hdr = Image.open("app/img/chk_hdr_new.png")
chk_new_hdr_hash = imagehash.average_hash(chk_new_hdr)
atmos_box = Image.open("app/img/chk_atmos.png")
chk_atmos_hash = imagehash.average_hash(atmos_box)
dtsx_box = Image.open("app/img/chk_dtsx.png")
chk_dtsx_hash = imagehash.average_hash(dtsx_box)