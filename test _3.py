import colorsys
from ftplib import FTP
import json
import pickle
import requests
from os import path
import json
import ntpath
import cv2
import copy
import shutil
import os
import glob
import shutil
import os.path
from os import path
import subprocess
import random
from difflib import SequenceMatcher

db = None
ftp_connect = None
# ocr_link = "https://vcaiapi.cognitiveservices.azure.com//vision/v2.0/recognizeText"
# ocr_key = "a62c68a79b754706bffddf775ab94872"


# ocr_link = os.environ['ocr_link']
# ocr_key = os.environ['ocr_key']
ocr_link="https://vcaiapi.cognitiveservices.azure.com//vision/v2.0/recognizeText"
ocr_key="a62c68a79b754706bffddf775ab94872"
#guideline_link = os.environ['guideline_url']
response_url = os.environ['response_url']
guideline_link="http://orientaluat.vahancheck.com/VCWebAPI/api/AI/AIQCGuideLine"

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def check_print(pred_mask,pred_mask_d):
  l2 = list(pred_mask.shape)
  n2 = l2[0]
  l1 = list(pred_mask_d.shape)
  n1 = l1[0]
  w = l1[1]
  h = l1[2]
  percentage = []
  while n1:
    numerator = 0
    denominator = 0
    for i in range(n2):
      for j in range(w):
        for k in range(h):
          if pred_mask_d[n1-1][j][k]&pred_mask[i][j][k]:
            numerator = numerator + 1
          if pred_mask_d[n1-1][j][k]==True:
            denominator = denominator + 1
    #print(numerator)
   # print(denominator)
    
    try:
      p= (numerator/denominator)*100
      percentage.insert(0,p)
    except:
      percentage.insert(0,0)
    n1 = n1-1
  return percentage


def Validate_rc(analysis, p, c, e):
    check1 = "cng"
    check2 = "petrol"
    check3 = "disel"
    a = analysis
    p = p.replace(" ", "").lower()
    c = c.replace(" ", "").lower()
    e = e.replace(" ", "").lower()
    l = []
    for i in range(len(a)):
        b = a[i]['words']
        for j in range(len(b)):
            z = b[j]['text']
            l.append(z)
    for i in range(len(l)):
        l[i] = l[i].replace(" ", "")
        l[i] = l[i].replace("-", "")
        l[i] = l[i].replace("*", "")
        l[i] = l[i].replace("&", "")
        l[i] = l[i].replace(":", "")
        l[i] = l[i].replace(";", "")
        l[i] = l[i].replace(".", "")
        l[i] = l[i].lower()
    chassis = []
    engine = []
    number_plate = []
    cng = []
    petrol = []
    disel = []
    count = 0
    for i in range(0, len(l)):
        chassis.append(similar(l[i][-6:], c))
        engine.append(similar(l[i][-6:], e))
        number_plate.append(similar(l[i], p))
        cng.append(similar(l[i], check1))
        petrol.append(similar(l[i], check2))
        disel.append(similar(l[i], check3))
    cn = "Matched" if max(chassis) >= 0.8 else "Not Matched"
    en = "Matched" if max(engine) >= 0.8 else "Not Matched"
    np = "Matched" if max(number_plate) >= 0.8 else "Not Matched"
    cng_out = "Matched" if max(cng) >= 1.0 else "Not Matched"
    petrol_out = "Matched" if max(petrol) >= 0.8 else "Not Matched"
    disel_out = "Matched" if max(disel) >= 0.8 else "Not Matched"
    print(cn, en, np, cng_out, petrol_out, disel_out)
    rc_match_list = [cn, en, np, cng_out, petrol_out, disel_out]
    for i in range(0, len(rc_match_list)):
        if rc_match_list[i] == "Matched":
            count += 1
    return count
    # print(count)

















a=10

while a<=100:
    print("akshay changes the code here in test 3")

    a+=1





def video_car_response(mode, lead_id, missing_guideline):
    _lead = load_qc_json(lead_id)
    if mode == "Image":
        to_open = f"{lead_id}/Processed/missing/present.pkl"
        with open(to_open, "rb") as ft:
            obj_list = pickle.load(ft)
        message, count, missing = validate_missing_parts_car(obj_list, lead_id)
        X = [elem.strip() for elem in message.split(",")]
        image = cv2.imread(f"{lead_id}/Processed/DND/Dents/front.jpg")
        h = 30
        w = 40
        for i in range(len(X)):
            w = w + 30
            image = cv2.putText(image, X[i], (h, w), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 0, 0), 2, cv2.LINE_AA)
        get_the_name = f"{lead_id}/Processed/name_dict.pkl"
        with open(get_the_name, "rb") as f:
            all_names = pickle.load(f)
        write_path = all_names["front.jpg"]
        cv2.imwrite(f"{lead_id}/AI/{write_path}", image)
        _lead = get_missing_response_car(missing_guideline, count, lead_id, _lead)
    else:
        to_open = f"{lead_id}/Processed/missing/present.pkl"
        to_open_video = f"{lead_id}/AI_Video/video_present.pkl"
        with open(to_open, "rb") as ft:
            obj_list = pickle.load(ft)
        with open(to_open_video, "rb") as ft:
            obj_list2 = pickle.load(ft)
        message, count, missing = validate_missing_parts_car(obj_list, lead_id)
        message2, count2, missing2 = validate_missing_parts_car(obj_list2, lead_id)
        for key, val in count.items():
            if count2[key] > val:
                count[key] = count2[key]
        to_del = []
        for key in missing:
            if key not in missing2:
                to_del.append(key)
            elif missing[key] > missing2[key]:
                missing[key] = missing2[key]
        for i in to_del:
            del missing[i]
        # message, count, missing = validate_missing_parts_car(count1, lead_id)
        message = ""
        for key, val in missing.items():
            message += " " + str(val) + " " + str(key) + " " + "missing" + ","
        message = message.strip(",").strip()

        X = [elem.strip() for elem in message.split(",")]
        image = cv2.imread(f"{lead_id}/Processed/DND/Dents/front.jpg")
        h = 30
        w = 40
        for i in range(len(X)):
            w = w + 30
            image = cv2.putText(image, X[i], (h, w), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 0, 0), 2, cv2.LINE_AA)
        get_the_name = f"{lead_id}/Processed/name_dict.pkl"
        with open(get_the_name, "rb") as f:
            all_names = pickle.load(f)
        write_path = all_names["front.jpg"]
        cv2.imwrite(f"{lead_id}/AI/{write_path}", image)
        _lead = get_missing_response_car(missing_guideline, count, lead_id, _lead)
    if len(message.strip()) > 0:
        _lead["QC_remarks"] = _lead["QC_remarks"] + "," + message
        _lead["output_data"]["Missing_part_model"]["Remark"] = _lead["output_data"]["Missing_part_model"][
                                                                   "Remark"].strip("String") + "," + message
    save_qc_json(lead_id, _lead)
















def video_car_response(mode, lead_id, missing_guideline):
    _lead = load_qc_json(lead_id)
    if mode == "Image":
        to_open = f"{lead_id}/Processed/missing/present.pkl"
        with open(to_open, "rb") as ft:
            obj_list = pickle.load(ft)
        message, count, missing = validate_missing_parts_car(obj_list, lead_id)
        X = [elem.strip() for elem in message.split(",")]
        image = cv2.imread(f"{lead_id}/Processed/DND/Dents/front.jpg")
        h = 30
        w = 40
        for i in range(len(X)):
            w = w + 30
            image = cv2.putText(image, X[i], (h, w), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 0, 0), 2, cv2.LINE_AA)
        get_the_name = f"{lead_id}/Processed/name_dict.pkl"
        with open(get_the_name, "rb") as f:
            all_names = pickle.load(f)
        write_path = all_names["front.jpg"]
        cv2.imwrite(f"{lead_id}/AI/{write_path}", image)
        _lead = get_missing_response_car(missing_guideline, count, lead_id, _lead)
    else:
        to_open = f"{lead_id}/Processed/missing/present.pkl"
        to_open_video = f"{lead_id}/AI_Video/video_present.pkl"
        with open(to_open, "rb") as ft:
            obj_list = pickle.load(ft)
        with open(to_open_video, "rb") as ft:
            obj_list2 = pickle.load(ft)
        message, count, missing = validate_missing_parts_car(obj_list, lead_id)
        message2, count2, missing2 = validate_missing_parts_car(obj_list2, lead_id)
        for key, val in count.items():
            if count2[key] > val:
                count[key] = count2[key]
        to_del = []
        for key in missing:
            if key not in missing2:
                to_del.append(key)
            elif missing[key] > missing2[key]:
                missing[key] = missing2[key]
        for i in to_del:
            del missing[i]
        # message, count, missing = validate_missing_parts_car(count1, lead_id)
        message = ""
        for key, val in missing.items():
            message += " " + str(val) + " " + str(key) + " " + "missing" + ","
        message = message.strip(",").strip()

        X = [elem.strip() for elem in message.split(",")]
        image = cv2.imread(f"{lead_id}/Processed/DND/Dents/front.jpg")
        h = 30
        w = 40
        for i in range(len(X)):
            w = w + 30
            image = cv2.putText(image, X[i], (h, w), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 0, 0), 2, cv2.LINE_AA)
        get_the_name = f"{lead_id}/Processed/name_dict.pkl"
        with open(get_the_name, "rb") as f:
            all_names = pickle.load(f)
        write_path = all_names["front.jpg"]
        cv2.imwrite(f"{lead_id}/AI/{write_path}", image)
        _lead = get_missing_response_car(missing_guideline, count, lead_id, _lead)
    if len(message.strip()) > 0:
        _lead["QC_remarks"] = _lead["QC_remarks"] + "," + message
        _lead["output_data"]["Missing_part_model"]["Remark"] = _lead["output_data"]["Missing_part_model"][
                                                                   "Remark"].strip("String") + "," + message
    save_qc_json(lead_id, _lead)
















def random_colors(N, bright=True):
    brightness = 1.0 if bright else 0.7
    hsv = [(i / N, 1, brightness) for i in range(N)]
    colors = list(map(lambda c: colorsys.hsv_to_rgb(*c), hsv))
    random.shuffle(colors)
    return colors


def fix_time(lead_id):
    _lead = load_qc_json(lead_id)
    time_path = f"{lead_id}/processing_time.json"
    with open(time_path, "r") as ft:
        pro_time = json.load(ft)
    try:
        _lead["output_data"]["Image_caption"]["Processing Time"] = pro_time['Image Captioning']
        _lead["output_data"]["vehicle_type_model"]["Processing Time"] = pro_time['Vehicle_type']
        _lead["output_data"]["Missing_part_model"]["Processing Time"] = pro_time["Missing_model"]
        _lead["output_data"]["Police_detection"]["Processing Time"] = pro_time["Police_garage"]
        _lead["output_data"]["Garage_Detection"]["Processing Time"] = pro_time["Police_garage"]
        _lead["output_data"]["Chassis_model"]["Processing Time"] = pro_time["Chassis_model"]
        _lead["output_data"]["RC_Model"]["Processing Time"] = pro_time["RC"]
        _lead["output_data"]["DND"]["Processing Time"] = pro_time["DND"]
        _lead["output_data"]["Number_Plate_Model"]["Processing Time"] = pro_time["Number_Plate"]
        _lead["output_data"]["Odometer_Model"]["Processing Time"] = pro_time["Odometer"]
        _lead["output_data"]["Rpm_Model"]["Processing Time"] = pro_time["RPM"]
        _lead["output_data"]["Windshield"]["Processing Time"] = pro_time["Windshield"]
    except Exception as e:
        print(e)
    save_qc_json(lead_id, _lead)


def Guideline_wrapper(obj):
    final = dict()
    for i in obj:
        if i["AgencyCode"] not in final:
            final[i["AgencyCode"]] = dict()
        if i["VehicleType"] not in final[i["AgencyCode"]]:
            final[i["AgencyCode"]][i["VehicleType"]] = dict()

    for j in obj:  # Extracting number from string
        try:
            j["AvgAllowedPercentageOrCount"] = float(
                ''.join(filter(lambda i_1: i_1.isdigit() or i_1 == ".", j["AvgAllowedPercentageOrCount"])))
        except:
            j["AvgAllowedPercentageOrCount"] = 50.0

    for i in obj:
        if i["Panel"] == "Customer First Name with RC Book (Matched with Input Parameter)":
            if "RC Book" not in final[i["AgencyCode"]][i["VehicleType"]]:
                final[i["AgencyCode"]][i["VehicleType"]]["RC Book"] = dict()
            if "First_name" not in final[i["AgencyCode"]][i["VehicleType"]]["RC Book"]:  # First Name in RC
                final[i["AgencyCode"]][i["VehicleType"]]["RC Book"]["First_name"] = dict()
                final[i["AgencyCode"]][i["VehicleType"]]["RC Book"]["First_name"]["Allowed"] = i[
                    "AvgAllowedPercentageOrCount"]
                final[i["AgencyCode"]][i["VehicleType"]]["RC Book"]["First_name"]["IsActive"] = i["IsActive"]
                final[i["AgencyCode"]][i["VehicleType"]]["RC Book"]["First_name"][
                    "Remark"] = "First name not mached with input"
                final[i["AgencyCode"]][i["VehicleType"]]["RC Book"]["First_name"]["Hold_type"] = i["HoldTypeWheightage"]

        if i["Panel"] == "Customer Last Name with RC Book (Matched with Input Parameter)":  # Last Name in RC
            if "Last_name" not in final[i["AgencyCode"]][i["VehicleType"]]["RC Book"]:
                final[i["AgencyCode"]][i["VehicleType"]]["RC Book"]["Last_name"] = dict()
                final[i["AgencyCode"]][i["VehicleType"]]["RC Book"]["Last_name"]["Allowed"] = i[
                    "AvgAllowedPercentageOrCount"]
                final[i["AgencyCode"]][i["VehicleType"]]["RC Book"]["Last_name"]["IsActive"] = i["IsActive"]
                final[i["AgencyCode"]][i["VehicleType"]]["RC Book"]["Last_name"][
                    "Remark"] = "Last name not matched with input"
                final[i["AgencyCode"]][i["VehicleType"]]["RC Book"]["Last_name"]["Hold_type"] = i["HoldTypeWheightage"]

        if i["Panel"] == "CNG fitted but not endorsed in RC and vice versa":  # CNG in RC
            if "CNG" not in final[i["AgencyCode"]][i["VehicleType"]]["RC Book"]:
                final[i["AgencyCode"]][i["VehicleType"]]["RC Book"]["CNG"] = dict()
                final[i["AgencyCode"]][i["VehicleType"]]["RC Book"]["CNG"]["Allowed"] = i["AvgAllowedPercentageOrCount"]
                final[i["AgencyCode"]][i["VehicleType"]]["RC Book"]["CNG"]["IsActive"] = i["IsActive"]
                final[i["AgencyCode"]][i["VehicleType"]]["RC Book"]["CNG"]["Remark"] = "CNG Available"
                final[i["AgencyCode"]][i["VehicleType"]]["RC Book"]["CNG"]["Hold_type"] = i["HoldTypeWheightage"]

        if i["Panel"] == "Chassis Number img (Matched with RC Book Chassis No.)":  # CNG in RC
            if "Chassis" not in final[i["AgencyCode"]][i["VehicleType"]]["RC Book"]:
                final[i["AgencyCode"]][i["VehicleType"]]["RC Book"]["Chassis"] = dict()
                final[i["AgencyCode"]][i["VehicleType"]]["RC Book"]["Chassis"]["Allowed"] = i[
                    "AvgAllowedPercentageOrCount"]
                final[i["AgencyCode"]][i["VehicleType"]]["RC Book"]["Chassis"]["IsActive"] = i["IsActive"]
                final[i["AgencyCode"]][i["VehicleType"]]["RC Book"]["Chassis"][
                    "Remark"] = "Chassis number not matched with input with RC Book"
                final[i["AgencyCode"]][i["VehicleType"]]["RC Book"]["Chassis"]["Hold_type"] = i["HoldTypeWheightage"]

        if i["Panel"] == "Registration Number with RC Book (Matched with Input Parameter)":  # Registration with RC
            if "Registration_number" not in final[i["AgencyCode"]][i["VehicleType"]]["RC Book"]:
                final[i["AgencyCode"]][i["VehicleType"]]["RC Book"]["Registration_number"] = dict()
                final[i["AgencyCode"]][i["VehicleType"]]["RC Book"]["Registration_number"]["Allowed"] = i[
                    "AvgAllowedPercentageOrCount"]
                final[i["AgencyCode"]][i["VehicleType"]]["RC Book"]["Registration_number"]["IsActive"] = i["IsActive"]
                final[i["AgencyCode"]][i["VehicleType"]]["RC Book"]["Registration_number"][
                    "Remark"] = "Registration Number not Matched with RC"
                final[i["AgencyCode"]][i["VehicleType"]]["RC Book"]["Registration_number"]["Hold_type"] = i[
                    "HoldTypeWheightage"]

        if i["Panel"] == "Engine Number (Matched with Input Parameter)":  # Engine number  with RC
            if "Engine_number" not in final[i["AgencyCode"]][i["VehicleType"]]["RC Book"]:
                final[i["AgencyCode"]][i["VehicleType"]]["RC Book"]["Engine_number"] = dict()
                final[i["AgencyCode"]][i["VehicleType"]]["RC Book"]["Engine_number"]["Allowed"] = i[
                    "AvgAllowedPercentageOrCount"]
                final[i["AgencyCode"]][i["VehicleType"]]["RC Book"]["Engine_number"]["IsActive"] = i["IsActive"]
                final[i["AgencyCode"]][i["VehicleType"]]["RC Book"]["Engine_number"][
                    "Remark"] = "Engine number not matched with RC"
                final[i["AgencyCode"]][i["VehicleType"]]["RC Book"]["Engine_number"]["Hold_type"] = i[
                    "HoldTypeWheightage"]

        if i["Panel"] == "RC Book image not available":  # RC image not available
            if "RC_availability" not in final[i["AgencyCode"]][i["VehicleType"]]["RC Book"]:
                final[i["AgencyCode"]][i["VehicleType"]]["RC Book"]["RC_availability"] = dict()
                final[i["AgencyCode"]][i["VehicleType"]]["RC Book"]["RC_availability"]["Allowed"] = i[
                    "AvgAllowedPercentageOrCount"]
                final[i["AgencyCode"]][i["VehicleType"]]["RC Book"]["RC_availability"]["IsActive"] = i["IsActive"]
                final[i["AgencyCode"]][i["VehicleType"]]["RC Book"]["RC_availability"][
                    "Remark"] = "RC book image not Available"
                final[i["AgencyCode"]][i["VehicleType"]]["RC Book"]["RC_availability"]["Hold_type"] = i[
                    "HoldTypeWheightage"]

        if i["Panel"] == "RC Book image not clear":  # RC image not clear
            if "RC_img_clear" not in final[i["AgencyCode"]][i["VehicleType"]]["RC Book"]:
                final[i["AgencyCode"]][i["VehicleType"]]["RC Book"]["RC_img_clear"] = dict()
                final[i["AgencyCode"]][i["VehicleType"]]["RC Book"]["RC_img_clear"]["Allowed"] = i[
                    "AvgAllowedPercentageOrCount"]
                final[i["AgencyCode"]][i["VehicleType"]]["RC Book"]["RC_img_clear"]["IsActive"] = i["IsActive"]
                final[i["AgencyCode"]][i["VehicleType"]]["RC Book"]["RC_img_clear"]["Remark"] = "RC image not clear"
                final[i["AgencyCode"]][i["VehicleType"]]["RC Book"]["RC_img_clear"]["Hold_type"] = i[
                    "HoldTypeWheightage"]

        if i["Panel"] == "Registration Number with Reg. image (Matched with Input Parameter)":  # Number plate model
            if "Registration_number" not in final[i["AgencyCode"]][i["VehicleType"]]:
                final[i["AgencyCode"]][i["VehicleType"]]["Registration_number"] = dict()
                final[i["AgencyCode"]][i["VehicleType"]]["Registration_number"]["Allowed"] = i[
                    "AvgAllowedPercentageOrCount"]
                final[i["AgencyCode"]][i["VehicleType"]]["Registration_number"]["IsActive"] = i["IsActive"]
                final[i["AgencyCode"]][i["VehicleType"]]["Registration_number"][
                    "Remark"] = "Registration number not matched Registration image"
                final[i["AgencyCode"]][i["VehicleType"]]["Registration_number"]["Hold_type"] = i["HoldTypeWheightage"]
        # Changing here for video guideline

        if i["Panel"] == "Identify  that Photos and Video is of same vehicle":  # Number plate model
            final[i["AgencyCode"]][i["VehicleType"]]["Registration_number"]["Video_Hold_type"] = i["HoldTypeWheightage"]
            final[i["AgencyCode"]][i["VehicleType"]]["Registration_number"]["Video_Is_active"] = i["IsActive"]

        if i["Panel"] == "Chassis Number (Matched with Input Parameter)":  # Chassis  model
            if "Chassis_number" not in final[i["AgencyCode"]][i["VehicleType"]]:
                final[i["AgencyCode"]][i["VehicleType"]]["Chassis_number"] = dict()
                final[i["AgencyCode"]][i["VehicleType"]]["Chassis_number"]["Allowed"] = i["AvgAllowedPercentageOrCount"]
                final[i["AgencyCode"]][i["VehicleType"]]["Chassis_number"]["IsActive"] = i["IsActive"]
                final[i["AgencyCode"]][i["VehicleType"]]["Chassis_number"][
                    "Remark"] = "Chassis number not matched with chassis image"
                final[i["AgencyCode"]][i["VehicleType"]]["Chassis_number"]["Hold_type"] = i["HoldTypeWheightage"]

        if i["Panel"] == "ODO Meter (Matched with Input Parameter)":  # odo  model
            if "Odometer_number" not in final[i["AgencyCode"]][i["VehicleType"]]:
                final[i["AgencyCode"]][i["VehicleType"]]["Odometer_number"] = dict()
                final[i["AgencyCode"]][i["VehicleType"]]["Odometer_number"]["Allowed"] = i[
                    "AvgAllowedPercentageOrCount"]
                final[i["AgencyCode"]][i["VehicleType"]]["Odometer_number"]["IsActive"] = i["IsActive"]
                final[i["AgencyCode"]][i["VehicleType"]]["Odometer_number"][
                    "Remark"] = "Odometer number not matched with image"
                final[i["AgencyCode"]][i["VehicleType"]]["Odometer_number"]["Hold_type"] = i["HoldTypeWheightage"]

        if i["Panel"] == "RPM ON/OFF":  # RPM model
            if "RPM" not in final[i["AgencyCode"]][i["VehicleType"]]:
                final[i["AgencyCode"]][i["VehicleType"]]["RPM"] = dict()
                final[i["AgencyCode"]][i["VehicleType"]]["RPM"]["Allowed"] = i["AvgAllowedPercentageOrCount"]
                final[i["AgencyCode"]][i["VehicleType"]]["RPM"]["IsActive"] = i["IsActive"]
                final[i["AgencyCode"]][i["VehicleType"]]["RPM"]["Remark"] = "RPM is off"
                final[i["AgencyCode"]][i["VehicleType"]]["RPM"]["Hold_type"] = i["HoldTypeWheightage"]

        if i["Panel"] == "Vehicle at Garage":  # Vehicle at garage model
            if "Garage" not in final[i["AgencyCode"]][i["VehicleType"]]:
                final[i["AgencyCode"]][i["VehicleType"]]["Garage"] = dict()
                final[i["AgencyCode"]][i["VehicleType"]]["Garage"]["Allowed"] = i["AvgAllowedPercentageOrCount"]
                final[i["AgencyCode"]][i["VehicleType"]]["Garage"]["IsActive"] = i["IsActive"]
                final[i["AgencyCode"]][i["VehicleType"]]["Garage"]["Remark"] = "Vehicle is at Garage"
                final[i["AgencyCode"]][i["VehicleType"]]["Garage"]["Hold_type"] = i["HoldTypeWheightage"]

        if i["Panel"] == "Vehicle at Police Station":  # Vehicle at garage model
            if "Police" not in final[i["AgencyCode"]][i["VehicleType"]]:
                final[i["AgencyCode"]][i["VehicleType"]]["Police"] = dict()
                final[i["AgencyCode"]][i["VehicleType"]]["Police"]["Allowed"] = i["AvgAllowedPercentageOrCount"]
                final[i["AgencyCode"]][i["VehicleType"]]["Police"]["IsActive"] = i["IsActive"]
                final[i["AgencyCode"]][i["VehicleType"]]["Police"]["Remark"] = "Vehicle is at Police Station"
                final[i["AgencyCode"]][i["VehicleType"]]["Police"]["Hold_type"] = i["HoldTypeWheightage"]

        if i["Panel"] == "Side view mirrors":  # Missing part model (sv)
            if "Missing_part" not in final[i["AgencyCode"]][i["VehicleType"]]:
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"] = dict()
            if "Side_view" not in final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]:
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["Side_view"] = dict()
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["Side_view"]["Allowed"] = i[
                    "AvgAllowedPercentageOrCount"]
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["Side_view"]["IsActive"] = i["IsActive"]
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["Side_view"][
                    "Remark"] = "Side view mirrors missing"
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["Side_view"]["Hold_type"] = i[
                    "HoldTypeWheightage"]

        if i["Panel"] == "Bumper (front and back)":  # front and rear bumper
            if "front_bumper" not in final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]:
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["front_bumper"] = dict()
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["front_bumper"]["Allowed"] = i[
                                                                                                          "AvgAllowedPercentageOrCount"] / 2
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["front_bumper"]["IsActive"] = i["IsActive"]
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["front_bumper"]["Remark"] = "Bumper missing"
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["front_bumper"]["Hold_type"] = i[
                    "HoldTypeWheightage"]

            if "rear_bumper" not in final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]:
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["rear_bumper"] = dict()
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["rear_bumper"]["Allowed"] = i[
                                                                                                         "AvgAllowedPercentageOrCount"] / 2
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["rear_bumper"]["IsActive"] = i["IsActive"]
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["rear_bumper"]["Remark"] = "Bumper missing"
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["rear_bumper"]["Hold_type"] = i[
                    "HoldTypeWheightage"]

        if i["Panel"] == "Wipers":  # Wipers
            if "Wipers" not in final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]:
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["Wipers"] = dict()
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["Wipers"]["Allowed"] = i[
                    "AvgAllowedPercentageOrCount"]
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["Wipers"]["IsActive"] = i["IsActive"]
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["Wipers"]["Remark"] = "Wipers missing"
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["Wipers"]["Hold_type"] = i[
                    "HoldTypeWheightage"]

        if i[
            "Panel"] == "Headlights (front and back) - Head lamp/Tail lamp/Indicators/Fog Lamp (front and back)":  # front and rear lamps
            if "hl" not in final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]:
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["hl"] = dict()
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["hl"]["Allowed"] = i[
                    "AvgAllowedPercentageOrCount"]
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["hl"]["IsActive"] = i["IsActive"]
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["hl"][
                    "Remark"] = "Head lamp/Tail lamp/Indicators/Fog Lamp missing"
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["hl"]["Hold_type"] = i["HoldTypeWheightage"]

            if "tl" not in final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]:
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["tl"] = dict()
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["tl"]["Allowed"] = i[
                    "AvgAllowedPercentageOrCount"]
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["tl"]["IsActive"] = i["IsActive"]
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["tl"][
                    "Remark"] = "Head lamp/Tail lamp/Indicators/Fog Lamp missing"
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["tl"]["Hold_type"] = i["HoldTypeWheightage"]

        if i["Panel"] == "Wheels (4)":  # Wheels
            if "Wheels" not in final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]:
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["Wheels"] = dict()
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["Wheels"]["Allowed"] = i[
                    "AvgAllowedPercentageOrCount"]
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["Wheels"]["IsActive"] = i["IsActive"]
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["Wheels"]["Remark"] = "Wheels missing"
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["Wheels"]["Hold_type"] = i[
                    "HoldTypeWheightage"]

        if i["Panel"] == "Silencer":  # Silencer
            if "Silencer" not in final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]:
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["Silencer"] = dict()
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["Silencer"]["Allowed"] = i[
                    "AvgAllowedPercentageOrCount"]
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["Silencer"]["IsActive"] = i["IsActive"]
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["Silencer"]["Remark"] = "Silencer missing"
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["Silencer"]["Hold_type"] = i[
                    "HoldTypeWheightage"]

        if i["Panel"] == "Wheels (2)":  # Wheels 2wh
            if "Wheels" not in final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]:
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["Wheels"] = dict()
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["Wheels"]["Allowed"] = i[
                    "AvgAllowedPercentageOrCount"]
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["Wheels"]["IsActive"] = i["IsActive"]
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["Wheels"]["Remark"] = "Wheels missing"
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["Wheels"]["Hold_type"] = i[
                    "HoldTypeWheightage"]

        if i["Panel"] == "Seat":  # seat 2 wh
            if "Seat" not in final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]:
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["Seat"] = dict()
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["Seat"]["Allowed"] = i[
                    "AvgAllowedPercentageOrCount"]
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["Seat"]["IsActive"] = i["IsActive"]
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["Seat"]["Remark"] = "Seat missing"
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["Seat"]["Hold_type"] = i["HoldTypeWheightage"]

        if i[
            "Panel"] == "Headlights (front and back) - Head lamp/Tail lamp/Indicators (front and back)":  # front and rear lamps 2wh
            if "hl" not in final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]:
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["hl"] = dict()
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["hl"]["Allowed"] = i[
                    "AvgAllowedPercentageOrCount"]
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["hl"]["IsActive"] = i["IsActive"]
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["hl"][
                    "Remark"] = "Head lamp/Tail lamp/Indicators missing"
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["hl"]["Hold_type"] = i["HoldTypeWheightage"]

            if "tl" not in final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]:
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["tl"] = dict()
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["tl"]["Allowed"] = i[
                    "AvgAllowedPercentageOrCount"]
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["tl"]["IsActive"] = i["IsActive"]
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["tl"][
                    "Remark"] = "Head lamp/Tail lamp/Indicators missing"
                final[i["AgencyCode"]][i["VehicleType"]]["Missing_part"]["tl"]["Hold_type"] = i["HoldTypeWheightage"]

        if i["Panel"] == "Front Panel":  # DND front panel
            if "DND" not in final[i["AgencyCode"]][i["VehicleType"]]:
                final[i["AgencyCode"]][i["VehicleType"]]["DND"] = dict()
            if "front_panel" not in final[i["AgencyCode"]][i["VehicleType"]]["DND"]:
                final[i["AgencyCode"]][i["VehicleType"]]["DND"]["front_panel"] = dict()
                final[i["AgencyCode"]][i["VehicleType"]]["DND"]["front_panel"]["Allowed"] = i[
                    "AvgAllowedPercentageOrCount"]
                final[i["AgencyCode"]][i["VehicleType"]]["DND"]["front_panel"]["IsActive"] = i["IsActive"]
                final[i["AgencyCode"]][i["VehicleType"]]["DND"]["front_panel"][
                    "Remark"] = "Damage detected in front panel"
                final[i["AgencyCode"]][i["VehicleType"]]["DND"]["front_panel"]["Hold_type"] = i["HoldTypeWheightage"]

        if i["Panel"] == "Front Right Side Panel":  # DND front right side
            if "Front_right_side" not in final[i["AgencyCode"]][i["VehicleType"]]["DND"]:
                final[i["AgencyCode"]][i["VehicleType"]]["DND"]["Front_right_side"] = dict()
                final[i["AgencyCode"]][i["VehicleType"]]["DND"]["Front_right_side"]["Allowed"] = i[
                    "AvgAllowedPercentageOrCount"]
                final[i["AgencyCode"]][i["VehicleType"]]["DND"]["Front_right_side"]["IsActive"] = i["IsActive"]
                final[i["AgencyCode"]][i["VehicleType"]]["DND"]["Front_right_side"][
                    "Remark"] = "Damage detected in Front Right Side panel"
                final[i["AgencyCode"]][i["VehicleType"]]["DND"]["Front_right_side"]["Hold_type"] = i[
                    "HoldTypeWheightage"]

        if i["Panel"] == "Front Left Side Panel":  # DND front left side
            if "Front_left_side" not in final[i["AgencyCode"]][i["VehicleType"]]["DND"]:
                final[i["AgencyCode"]][i["VehicleType"]]["DND"]["Front_left_side"] = dict()
                final[i["AgencyCode"]][i["VehicleType"]]["DND"]["Front_left_side"]["Allowed"] = i[
                    "AvgAllowedPercentageOrCount"]
                final[i["AgencyCode"]][i["VehicleType"]]["DND"]["Front_left_side"]["IsActive"] = i["IsActive"]
                final[i["AgencyCode"]][i["VehicleType"]]["DND"]["Front_left_side"][
                    "Remark"] = "Damage detected in Front Left Side panel"
                final[i["AgencyCode"]][i["VehicleType"]]["DND"]["Front_left_side"]["Hold_type"] = i[
                    "HoldTypeWheightage"]

        if i["Panel"] == "Back Left Side Panel":  # DND back left side
            if "Back_left_side" not in final[i["AgencyCode"]][i["VehicleType"]]["DND"]:
                final[i["AgencyCode"]][i["VehicleType"]]["DND"]["Back_left_side"] = dict()
                final[i["AgencyCode"]][i["VehicleType"]]["DND"]["Back_left_side"]["Allowed"] = i[
                    "AvgAllowedPercentageOrCount"]
                final[i["AgencyCode"]][i["VehicleType"]]["DND"]["Back_left_side"]["IsActive"] = i["IsActive"]
                final[i["AgencyCode"]][i["VehicleType"]]["DND"]["Back_left_side"][
                    "Remark"] = "Damage detected in Back Left Side panel"
                final[i["AgencyCode"]][i["VehicleType"]]["DND"]["Back_left_side"]["Hold_type"] = i["HoldTypeWheightage"]

        if i["Panel"] == "Back Right Side Panel":  # DND front left side
            if "Back_right_side" not in final[i["AgencyCode"]][i["VehicleType"]]["DND"]:
                final[i["AgencyCode"]][i["VehicleType"]]["DND"]["Back_right_side"] = dict()
                final[i["AgencyCode"]][i["VehicleType"]]["DND"]["Back_right_side"]["Allowed"] = i[
                    "AvgAllowedPercentageOrCount"]
                final[i["AgencyCode"]][i["VehicleType"]]["DND"]["Back_right_side"]["IsActive"] = i["IsActive"]
                final[i["AgencyCode"]][i["VehicleType"]]["DND"]["Back_right_side"][
                    "Remark"] = "Damage detected in Back Right Side panel"
                final[i["AgencyCode"]][i["VehicleType"]]["DND"]["Back_right_side"]["Hold_type"] = i[
                    "HoldTypeWheightage"]

        if i["Panel"] == "Back Panel":  # DND front left side
            if "Back_panel" not in final[i["AgencyCode"]][i["VehicleType"]]["DND"]:
                final[i["AgencyCode"]][i["VehicleType"]]["DND"]["Back_panel"] = dict()
                final[i["AgencyCode"]][i["VehicleType"]]["DND"]["Back_panel"]["Allowed"] = i[
                    "AvgAllowedPercentageOrCount"]
                final[i["AgencyCode"]][i["VehicleType"]]["DND"]["Back_panel"]["IsActive"] = i["IsActive"]
                final[i["AgencyCode"]][i["VehicleType"]]["DND"]["Back_panel"][
                    "Remark"] = "Damage detected in Back panel"
                final[i["AgencyCode"]][i["VehicleType"]]["DND"]["Back_panel"]["Hold_type"] = i["HoldTypeWheightage"]

        if i["Panel"] == "Right Side Panel":  # DND front left side
            if "Right_side" not in final[i["AgencyCode"]][i["VehicleType"]]["DND"]:
                final[i["AgencyCode"]][i["VehicleType"]]["DND"]["Right_side"] = dict()
                final[i["AgencyCode"]][i["VehicleType"]]["DND"]["Right_side"]["Allowed"] = i[
                    "AvgAllowedPercentageOrCount"]
                final[i["AgencyCode"]][i["VehicleType"]]["DND"]["Right_side"]["IsActive"] = i["IsActive"]
                final[i["AgencyCode"]][i["VehicleType"]]["DND"]["Right_side"][
                    "Remark"] = "Damage detected in Right side panel"
                final[i["AgencyCode"]][i["VehicleType"]]["DND"]["Right_side"]["Hold_type"] = i["HoldTypeWheightage"]

        if i["Panel"] == "Left Side Panel":  # DND front left side
            if "Left_side" not in final[i["AgencyCode"]][i["VehicleType"]]["DND"]:
                final[i["AgencyCode"]][i["VehicleType"]]["DND"]["Left_side"] = dict()
                final[i["AgencyCode"]][i["VehicleType"]]["DND"]["Left_side"]["Allowed"] = i[
                    "AvgAllowedPercentageOrCount"]
                final[i["AgencyCode"]][i["VehicleType"]]["DND"]["Left_side"]["IsActive"] = i["IsActive"]
                final[i["AgencyCode"]][i["VehicleType"]]["DND"]["Left_side"][
                    "Remark"] = "Damage detected in Left side panel"
                final[i["AgencyCode"]][i["VehicleType"]]["DND"]["Left_side"]["Hold_type"] = i["HoldTypeWheightage"]

        if i["Panel"] == "All Panel":  # DND front left side
            if "All_Panel" not in final[i["AgencyCode"]][i["VehicleType"]]["DND"]:
                final[i["AgencyCode"]][i["VehicleType"]]["DND"]["All_Panel"] = dict()
                final[i["AgencyCode"]][i["VehicleType"]]["DND"]["All_Panel"]["Allowed"] = i[
                    "AvgAllowedPercentageOrCount"]
                final[i["AgencyCode"]][i["VehicleType"]]["DND"]["All_Panel"]["IsActive"] = i["IsActive"]
                final[i["AgencyCode"]][i["VehicleType"]]["DND"]["All_Panel"]["Remark"] = "Damage detected in All panel"
                final[i["AgencyCode"]][i["VehicleType"]]["DND"]["All_Panel"]["Hold_type"] = i["HoldTypeWheightage"]

        if i["Panel"] == "Windshield (front and back)" or i["Panel"].strip() == "Windshield":  # DND front left side
            if "Windshield" not in final[i["AgencyCode"]][i["VehicleType"]]:
                final[i["AgencyCode"]][i["VehicleType"]]["Windshield"] = dict()
                final[i["AgencyCode"]][i["VehicleType"]]["Windshield"]["Allowed"] = i[
                    "AvgAllowedPercentageOrCount"]
                final[i["AgencyCode"]][i["VehicleType"]]["Windshield"]["IsActive"] = i["IsActive"]
                final[i["AgencyCode"]][i["VehicleType"]]["Windshield"]["Remark"] = "Windshield not detected"
                final[i["AgencyCode"]][i["VehicleType"]]["Windshield"]["Hold_type"] = i["HoldTypeWheightage"]

        if i["Panel"] == "Vehicle Type Mismatch":  # DND front left side
            if "v_type" not in final[i["AgencyCode"]][i["VehicleType"]]:
                final[i["AgencyCode"]][i["VehicleType"]]["v_type"] = dict()
                final[i["AgencyCode"]][i["VehicleType"]]["v_type"]["Allowed"] = i[
                    "AvgAllowedPercentageOrCount"]
                final[i["AgencyCode"]][i["VehicleType"]]["v_type"]["IsActive"] = i["IsActive"]
                final[i["AgencyCode"]][i["VehicleType"]]["v_type"]["Remark"] = "Vehicle type not matched with input"
                final[i["AgencyCode"]][i["VehicleType"]]["v_type"]["Hold_type"] = i["HoldTypeWheightage"]
    return final


def_data = {
    "Image_caption": {
        "model_status": False,
        "model_result": {
            "First": [],
            "Second": []
        },
        "Remark": "String",
        "Processing Time": 0.0,
        "360_view": False
    },
    "vehicle_type_model": {
        "model_status": False,
        "model_result": "string",
        "vehicle_type_matches_with_input": False,
        "Remark": "String",
        "Processing Time": 0.0,
        "Video_Remarks": "NA",
        "Video_AIModelResultPercentage": "80%",
        "Video_AIQCStatus": "",
        "Video_NoOfDamageCount": "String",
        "Model_qc": "Approve"
    },
    "Missing_part_model": {
        "model_status": False,
        "model_result": "string",
        "Model_qc": "Approve",
        "missing_details": dict(Bumper={
            "result": "string",
            "remark": "string",
            'IsActive': 'False',
            "Model_qc": "Approve"
        }, Side_view={
            "result": "string",
            "remark": "string",
            'IsActive': 'False',
            "Model_qc": "Approve"
        }, Wheels={
            "result": "string",
            "remark": "string",
            'IsActive': 'False',
            "Model_qc": "Approve"
        }, Headlights={
            "result": "string",
            "remark": "string",
            'IsActive': 'False',
            "Model_qc": "Approve"
        }, Wipers={
            "result": "string",
            "remark": "string",
            'IsActive': 'False',
            "Model_qc": "Approve"
        }, Seat={
            "result": "string",
            "remark": "string",
            'IsActive': 'False',
            "Model_qc": "Approve"
        }, Silencer={
            "result": "string",
            "remark": "string",
            'IsActive': 'False',
            "Model_qc": "Approve"
        }),
        "Remark": "String",
        "Processing Time": 0.0,
        "Video_Remarks": "NA",
        "Video_AIModelResultPercentage": "80%",
        "Video_AIQCStatus": "Approve",
        "Video_NoOfDamageCount": "String"
    },
    "Police_detection": {
        "model_status": False,
        "model_result": "string",
        "Remark": "String",
        "Processing Time": 0.0,
        "Is_Active": False,
        "Video_Remarks": "NA",
        "Video_AIModelResultPercentage": "80%",
        "Video_AIQCStatus": "Approve",
        "Video_NoOfDamageCount": "String",
        "Model_qc": "Approve"
    },
    "Garage_Detection": {
        "model_status": False,
        "model_result": "string",
        "Remark": "String",
        "Processing Time": 0.0,
        "Is_Active": False,
        "Video_Remarks": "NA",
        "Video_AIModelResultPercentage": "80%",
        "Video_AIQCStatus": "Approve",
        "Video_NoOfDamageCount": "String",
        "Model_qc": "Approve"
    },
    "RC_Model": {
        "Chassis": {"model_status": False,
                    "model_result": "string",
                    "Chassis_Number_matches_with_input": False,
                    "Is_Active": False,
                    "Remark": "String",
                    "Model_qc": "Approve"
                    },
        "Engine": {"model_status": False,
                   "model_result": "string",
                   "Engine_Number_matches_with_input": False,
                   "Is_Active": False,
                   "Remark": "String",
                   "Model_qc": "Approve"
                   },
        "Registration": {"model_status": False,
                         "model_result": "string",
                         "Registration_Number_matches_with_input": False,
                         "Is_Active": False,
                         "Remark": "String",
                         "Model_qc": "Approve"
                         },
        "First_name": {"model_status": False,
                       "model_result": "string",
                       "First_name_matches_with_input": False,
                       "Is_Active": False,
                       "Remark": "String",
                       "Model_qc": "Approve"
                       },
        "Last_name": {"model_status": False,
                      "model_result": "string",
                      "Last_name_matches_with_input": False,
                      "Is_Active": False,
                      "Remark": "String",
                      "Model_qc": "Approve"
                      },
        "CNG": {"model_status": False,
                "model_result": "string",
                "Is_Active": False,
                "Remark": "String",
                "Model_qc": "Approve"
                },
        "RC_availability": {"model_status": False,
                            "model_result": "string",
                            "Is_Active": False,
                            "Remark": "String",
                            "Model_qc": "Approve"
                            },
        "RC_img_clear": {"model_status": False,
                         "model_result": "string",
                         "Is_Active": False,
                         "Remark": "String",
                         "Model_qc": "Approve"
                         },
        "Remark": "String",
        "Processing Time": 0.0
    },
    "Chassis_model": {
        "model_status": False,
        "model_result": "string",
        "Chassis_Number_matches_with_input": False,
        "Remark": "String",
        "Is_Active": False,
        "Processing Time": 0.0,
        "Video_Remarks": "NA",
        "Video_AIModelResultPercentage": "80%",
        "Video_AIQCStatus": "Approve",
        "Video_NoOfDamageCount": "String",
        "Model_qc": "Approve"
    },
    "Number_Plate_Model": {
        "model_status": False,
        "model_result": "string",
        "Number_plate_matches_with_input": False,
        "vehicle_type_from_plate": "string",
        "Remark": "String",
        "Is_Active": False,
        "Processing Time": 0.0,
        "Video_Remarks": "NA",
        "Video_AIModelResultPercentage": "80%",
        "Video_AIQCStatus": "Approve",
        "Video_NoOfDamageCount": "String",
        "Model_qc": "Approve"
    },
    "Odometer_Model": {
        "model_status": False,
        "model_result": "string",
        "Odometer_matches_with_input": False,
        "Remark": "String",
        "Is_Active": False,
        "Processing Time": 0.0,
        "Video_Remarks": "NA",
        "Video_AIModelResultPercentage": "80%",
        "Video_AIQCStatus": "Approve",
        "Video_NoOfDamageCount": "String",
        "Model_qc": "Approve"
    },
    "Rpm_Model": {
        "model_status": False,
        "model_result": "string",
        "needle_reading": "string",
        "Remark": "String",
        "Is_Active": False,
        "Processing Time": 0.0,
        "Video_Remarks": "NA",
        "Video_AIModelResultPercentage": "80%",
        "Video_AIQCStatus": "Approve",
        "Video_NoOfDamageCount": "String",
        "Model_qc": "Approve"
    },
    "Windshield": {
        "front": {"model_status": False,
                  "model_result": "string",
                  "Remark": "String"},
        "rear": {"model_status": False,
                 "model_result": "string",
                 "Remark": "String"},
        "Is_Active": False,
        "Processing Time": 0.0,
        "Video_Remarks": "NA",
        "Video_AIModelResultPercentage": "80%",
        "Video_AIQCStatus": "Approve",
        "Video_NoOfDamageCount": "String",
        "Model_qc": "Approve"
    },
    "DND": {
        "model_result": "string",
        "Total_Damages": 0,
        "panel_wise": {},
        "sub_panel_wise": {},
        "Remark": "String",
        "Is_Active": False,
        "Processing Time": 0.0,
        "Video_Remarks": "NA",
        "Video_AIModelResultPercentage": "80%",
        "Video_AIQCStatus": "Approve",
        "Video_NoOfDamageCount": "String",
        "Model_qc": "Approve"
    }
}


def validate_missing(a1, a2):
    c1 = []
    c1.extend(a1)
    c1.extend(a2)
    check = ['rear_right', 'right', 'rear', 'rear_left', 'left', 'front_left', 'front', "front_right", "odometer", "rc",
             "chassis"]
    msg = ""
    short = []
    to_respond = True
    for i in check:
        if i not in c1:
            short.append(i)
    if len(short) > 0:
        to_respond = False
        for t in short:
            msg += ", " + t
        msg += " " + "image missing"
        msg = msg.strip(",")
    return msg, to_respond


def validate_caption(c1, c2):
    msg = ""
    short = []
    to_respond = True
    all = []
    all.extend(c1)
    all.extend(c2)
    if "front" not in all:
        short.append("Front")
    if "chassis" not in all:
        short.append("Chassis")
    if "rc" not in all:
        short.append("RC")

    if len(short) > 0:
        to_respond = False
        for t in short:
            msg += "," + t
        msg += " " + "image missing"
        msg = msg.strip(",")

    if "RC" in short and len(short) > 1:
        msg = msg.replace(",RC", "")
        msg += ", RC Image either missing or mismatched with input"

    if "RC" in short and len(short) == 1:
        msg = "RC Image either missing or mismatched with input"

    return msg, to_respond


def validate_lead(l):
    msg = ""
    all_control = []
    to_respond = True
    k = l["input_data"]
    print("This is inside validate", type(k))
    print(k.keys())
    if k['leadId'].lower() == "string" or k['leadId'].strip() == "":
        all_control.append("lead Id")
    if k['providerId'].lower() == "string" or k['providerId'].strip() == "":
        all_control.append("Provider")
    if k['vehicleType'].lower() == "string" or k['vehicleType'].strip() == "":
        all_control.append("Vehicle Type")
    if k['registrationNumber'].lower() == "string" or k['registrationNumber'].strip() == "":
        all_control.append("Registration Number")
    if k['chassisNumber'].lower() == "string" or k['chassisNumber'].strip() == "":
        all_control.append("Chassis Number")
    if k['engineNumber'].lower() == "string" or k['engineNumber'].strip() == "":
        all_control.append("Engine Number")
    if k['odometerReading'].lower() == "string" or k['odometerReading'].strip() == "":
        all_control.append("Odometer Reading")
    if k['name'].lower() == "string" or k['name'].strip() == "":
        all_control.append("Name")

    if len(all_control) > 0:
        to_respond = False
        for t in all_control:
            msg += "," + t
        msg += " " + "missing in input data"
        msg = msg.strip(",")
    return msg, to_respond


def save_qc_json(lead_id, _lead):
    try:
        with open(lead_id + "/QC_Result.json", "w")as fout:
            json.dump(_lead, fout)
    except Exception as e:
        print(e)


def load_qc_json(lead_id):
    try:
        with open(lead_id + "/QC_Result.json", "r")as fout:
            data = json.load(fout)
        return data
    except Exception as e:
        print(e)
        return 0


def load_vahan_qc_json(lead_id):
    try:
        with open(lead_id + "/Processed/Vahan_qc.json", "r")as fout:
            data = json.load(fout)
        return data
    except Exception as e:
        print(e)
        return 0


def validate_missing_parts_car(c1, lead_id):
    print("Response from missing model", c1)
    found_count = dict()
    missing = dict()
    #########################################################
    wheel1 = ["right", "front_right", "rear_right"]
    wheel2 = ["left", "front_left", "rear_left"]

    wheel1_status = []
    wheel2_status = []

    for angle in wheel1:
        if angle in c1:
            wheel1_status.append(c1[angle].count("wheel"))
            print(angle, wheel1_status)
    for angle in wheel2:
        if angle in c1:
            wheel2_status.append(c1[angle].count("wheel"))
            print(angle, wheel2_status)

    if len(wheel1_status) == 0:
        missing["right_side_wheel"] = 2
        found_count["right_side_wheel"] = 0
    if len(wheel2_status) == 0:
        missing["left_side_wheel"] = 2
        found_count["left_side_wheel"] = 0

    if len(wheel1_status) > 0:
        wheel1_count = max(wheel1_status)
        print("right side wheel count ", wheel1_count)
        found_count["right_side_wheel"] = wheel1_count
        if wheel1_count < 2:
            missing["right_side_wheel"] = 2 - wheel1_count

    if len(wheel2_status) > 0:
        wheel2_count = max(wheel2_status)
        print("left side wheel count ", wheel2_count)
        found_count["left_side_wheel"] = wheel2_count
        if wheel2_count < 2:
            missing["left_side_wheel"] = 2 - wheel2_count

    ########################################################################
    wip = ["front"]
    wip_sta = 0
    for angle in wip:
        print(angle)
        if angle in c1:
            wip_sta = c1[angle].count("wipers")
            found_count["wipers"] = wip_sta
            if wip_sta == 0:
                print("Inside wiper check")
                if "front_left" in c1:
                    print("inside front left")
                    if c1["front_left"].count("wipers") >= 1:
                        wip_sta = 1
                        found_count["wipers"] = 1
                if wip_sta == 0 and "front_right" in c1:
                    print("inside front right")
                    if c1["front_right"].count("wipers") >= 1:
                        wip_sta = 1
                        found_count["wipers"] = 1

        if "front_left" in c1:
            print("inside front left")
            if c1["front_left"].count("wipers") >= 1:
                wip_sta = 1
                found_count["wipers"] = 1
        if wip_sta == 0 and "front_right" in c1:
            print("inside front right")
            if c1["front_right"].count("wipers") >= 1:
                wip_sta = 1
                found_count["wipers"] = 1
        if wip_sta == 0:
            print("else")
            missing["wipers"] = " "
            found_count["wipers"] = 0
    if wip_sta < 1:
        missing["wipers"] = " "
        found_count["wipers"] = 0

    ###########################################################################
    h_sta = 0
    try:
        if "front" in c1:
            h_sta = c1["front"].count("hl")
        found_count["hl"] = h_sta
        if h_sta < 2:
            if "front_left" in c1 and "front_right" in c1:
                if c1["front_left"].count("hl") >= 1 and c1["front_right"].count("hl") >= 1:
                    found_count["hl"] = 2
                    h_sta = 2
            if "front_left" in c1 and found_count["hl"] == 0:
                if c1["front_left"].count("hl") >= 1:
                    found_count["hl"] = 1
                    h_sta = 1
            if "front_right" in c1 and found_count["hl"] == 0:
                if c1["front_right"].count("hl") >= 1:
                    found_count["hl"] = 1
                    h_sta = 1
            if h_sta < 2:
                missing["front hl"] = 2 - h_sta
    except:
        found_count["hl"] = 0
        missing["front hl"] = 2
        if "front_left" in c1 and "front_right" in c1:
            if c1["front_left"].count("hl") >= 1 and c1["front_right"].count("hl") >= 1:
                found_count["hl"] = 2
                if "front hl" in missing:
                    del missing["front hl"]
        pass
    print("Front hl", found_count["hl"])

    ###########################################################################
    try:
        f_bu = c1["front"].count("bumper")
        found_count["f_bumper"] = f_bu
        if f_bu < 1:
            found_count["f_bumper"] = 0
            missing["front bumper"] = ""
    except:
        found_count["f_bumper"] = 0
        missing["front bumper"] = ""
        pass
    print("Front bumper", found_count["f_bumper"])
    ##########################################################################
    if found_count["f_bumper"] == 0:
        print("Inside the check")
        to_open = f"{lead_id}/Processed/DND/angle.pkl"
        print("TO open", to_open)
        with open(to_open, "rb") as ft:
            all_an = pickle.load(ft)
            print(all_an)
            if "front" in all_an:
                print("Checking in front")
                print("*" * 50)
                if "f_bumper" in all_an["front"]:
                    found_count["f_bumper"] = 1
                    del missing["front bumper"]
                    print("FOund bumper in subpanel")

            if found_count["f_bumper"] == 0 and "front_left" in all_an:
                print("Checking in front_left")
                print("*" * 50)
                if "f_bumper" in all_an["front_left"]:
                    found_count["f_bumper"] = 1
                    del missing["front bumper"]
                    print("FOund bumper in subpanel")
            if found_count["f_bumper"] == 0 and "front_right" in all_an:
                print("Checking in front_right")
                print("*" * 50)
                if "f_bumper" in all_an["front_right"]:
                    found_count["f_bumper"] = 1
                    del missing["front bumper"]
                    print("FOund bumper in subpanel")

    print("Tail prediction")
    tail_l = ["rear"]
    t_count = 0
    for angle in tail_l:
        if angle in c1:
            t_count = c1[angle].count("tl")
            found_count["tail_lamp"] = t_count
            print("tail lamp", t_count)
        else:
            missing["tail lamp "] = 2
            found_count["tail_lamp"] = 0

    if t_count < 2:
        if "rear_left" in c1 and "rear_right" in c1:
            if c1["rear_left"].count("tl") >= 1 and c1["rear_right"].count("tl") >= 1:
                found_count["tail_lamp"] = 2
                if "tail lamp " in missing:
                    del missing["tail lamp "]

    if found_count["tail_lamp"] == 0:
        if "rear_left" in c1:
            if c1["rear_left"].count("tl") >= 1:
                t_count = 1
                found_count["tail_lamp"] = 1
        if "rear_right" in c1 and t_count < 1:
            if c1["rear_right"].count("tl") >= 1:
                t_count = 1
                found_count["tail_lamp"] = 1

    if found_count["tail_lamp"] < 2:
        missing["tail lamp "] = 2 - t_count
        found_count["tail_lamp"] = t_count
    #########################################################################

    t_bumpe = ["rear"]
    t_bu = 0
    for angle in t_bumpe:
        if angle in c1:
            t_bu = c1[angle].count("bumper")
            found_count["rear_bumper"] = t_bu
        else:
            missing["rear bumper"] = ""
            found_count["rear_bumper"] = 0
    if t_bu < 1:
        missing["rear bumper"] = ""
        found_count["rear_bumper"] = 0

    print(found_count["rear_bumper"])
    if found_count["rear_bumper"] == 0:
        to_open = f"{lead_id}/Processed/DND/angle.pkl"
        with open(to_open, "rb") as ft:
            all_an = pickle.load(ft)
            if "rear" in all_an:
                if "b_bumper" in all_an["rear"]:
                    found_count["rear_bumper"] = 1
                    if "rear bumper" in missing:
                        del missing["rear bumper"]
            if found_count["rear_bumper"] == 0 and "rear_left" in all_an:
                if "b_bumper" in all_an["rear_left"]:
                    found_count["rear_bumper"] = 1
                    if "rear bumper" in missing:
                        del missing["rear bumper"]

            if found_count["rear_bumper"] == 0 and "rear_right" in all_an:
                if "b_bumper" in all_an["rear_right"]:
                    found_count["rear_bumper"] = 1
                    if "rear bumper" in missing:
                        del missing["rear bumper"]

    ########################################################################

    sv1 = ["right", "front_right", "rear_right"]
    sv2 = ["left", "front_left", "rear_left"]

    sv1_status = []
    sv2_status = []

    for angle in sv1:
        if angle in c1:
            sv1_status.append(c1[angle].count("lsv"))
            sv1_status.append(c1[angle].count("rsv"))
    for angle in sv2:
        if angle in c1:
            sv2_status.append(c1[angle].count("lsv"))
            sv2_status.append(c1[angle].count("rsv"))

    print(sv1_status)
    print(sv2_status)

    if len(sv1_status) == 0:
        missing["rsv"] = 1
        found_count["rsv"] = 0
    if len(sv2_status) == 0:
        missing["lsv"] = 1
        found_count["lsv"] = 0

    if len(sv1_status) > 0:
        sv_count = max(sv1_status)
        found_count["rsv"] = sv_count
        if sv_count < 1:
            missing["rsv"] = 1
            found_count["rsv"] = 0

    if len(sv2_status) > 0:
        sv2_count = max(sv2_status)
        found_count["lsv"] = sv2_count
        if sv2_count < 1:
            missing["lsv"] = 1
            found_count["lsv"] = 0
    #######################################################################
    print("missing", missing)

    msg = ""
    for key, val in missing.items():
        msg += " " + str(val) + " " + str(key) + " " + "missing" + ","
    msg = msg.strip(",").strip()
    print(found_count)
    return msg, found_count, missing


def validate_missing_parts_two(c1):
    found_count = dict()
    missing = dict()
    #########################################################
    all_available_angle = c1.keys()
    all_angle = dict()
    parts = ["sv", 'indicator', "hl", "wheel", "seat", "sil", "tl"]
    for angle in all_available_angle:
        all_angle[angle] = dict()
        for i in parts:
            all_angle[angle][i] = c1[angle].count(i)
    print(all_angle)
    wheel_holder = []
    ##########################################################3
    if "front" in all_angle and "rear" in all_angle:
        print("inside if")
        if all_angle["front"]["wheel"] == 1 and all_angle["rear"]["wheel"] == 1:
            found_count["Wheel"] = 2
        else:
            print("Inside ifelse")
            if "right" in all_angle:
                wheel_holder.append(all_angle["right"]["wheel"])
            print("right", wheel_holder)
            if "left" in all_angle:
                wheel_holder.append(all_angle["left"]["wheel"])
            if len(wheel_holder) > 0:
                wheel_c = max(wheel_holder)
            else:
                wheel_c = 0
            print("left", wheel_holder)
            found_count["Wheel"] = wheel_c

    else:
        print("Inside else")
        if "right" in all_angle:
            wheel_holder.append(all_angle["right"]["wheel"])
        print(wheel_holder)
        if "left" in all_angle:
            wheel_holder.append(all_angle["left"]["wheel"])
        if len(wheel_holder) > 0:
            wheel_c = max(wheel_holder)
        else:
            wheel_c = 0
        print(wheel_holder)
        found_count["Wheel"] = wheel_c

    if found_count["Wheel"] == 0:
        if "front" in all_angle and "rear" in all_angle:
            if all_angle["front"]["wheel"] == 1 or all_angle["rear"]["wheel"] == 1:
                found_count["Wheel"] = 1
        elif "front" in all_angle:
            if all_angle["front"]["wheel"] >= 1:
                found_count["Wheel"] = 1
        elif "rear" in all_angle:
            if all_angle["rear"]["wheel"] >= 1:
                found_count["Wheel"] = 1
    if found_count["Wheel"] < 2:
        missing["Wheel"] = 2 - found_count["Wheel"]
    #######################################################################################
    found_count["hl"] = 0
    missing["hl"] = ""
    for key in all_angle.keys():
        if all_angle[key]["hl"] >= 1:
            found_count["hl"] = all_angle[key]["hl"]
            print(missing)
            if "hl" in missing:
                del missing["hl"]
    #######################################################################################
    found_count["tl"] = 0
    missing["tl"] = ""
    for key in all_angle.keys():
        if all_angle[key]["tl"] >= 1:
            found_count["tl"] = all_angle[key]["tl"]
            if "tl" in missing:
                del missing["tl"]
    #######################################################################################
    found_count["seat"] = 0
    missing["seat"] = ""
    for key in all_angle.keys():
        if all_angle[key]["seat"] >= 1:
            found_count["seat"] = all_angle[key]["seat"]
            if "seat" in missing:
                del missing["seat"]
    #########################################################################################
    found_count["sil"] = 0
    missing["sil"] = ""
    for key in all_angle.keys():
        if all_angle[key]["sil"] >= 1:
            found_count["sil"] = all_angle[key]["sil"]
            if "sil" in missing:
                del missing["sil"]
    # ###########################################################################################
    found_count["sv"] = 0
    missing["sv"] = 2
    print("running sv")
    for key in all_angle.keys():
        if all_angle[key]["sv"] >= 2:
            found_count["sv"] = all_angle[key]["sv"]
            if "sv" in missing:
                del missing["sv"]
        elif all_angle[key]["sv"] > found_count["sv"]:
            found_count["sv"] = all_angle[key]["sv"]
            if found_count["sv"] >= 2:
                if "sv" in missing:
                    del missing["sv"]
    if found_count["sv"] < 2:
        missing["sv"] = 2 - found_count["sv"]
    ############################################################################################
    found_count["front_indicators"] = 0
    missing["front_indicators"] = 2
    print("running front_indicators")

    for key in ["front", "front_right", "front_left"]:
        if key in all_angle.keys():
            if all_angle[key]["indicator"] >= 2:
                found_count["front_indicators"] = all_angle[key]["indicator"]
                if "front_indicators" in missing:
                    del missing["front_indicators"]
                    break
            elif all_angle[key]["indicator"] > found_count["front_indicators"]:
                found_count["front_indicators"] = all_angle[key]["indicator"]
                if found_count["front_indicators"] >= 2:
                    if "front_indicators" in missing:
                        del missing["front_indicators"]

    if found_count["front_indicators"] < 2:
        missing["front_indicators"] = 2 - found_count["front_indicators"]
    ###############################################################################################
    found_count["rear_indicators"] = 0
    missing["rear_indicators"] = 2
    print("running rear_indicators")

    for key in ["rear", "rear_right", "rear_left"]:
        if key in all_angle.keys():

            if all_angle[key]["indicator"] >= 2:
                found_count["rear_indicators"] = all_angle[key]["indicator"]
                if "rear_indicators" in missing:
                    del missing["rear_indicators"]

            elif all_angle[key]["indicator"] > found_count["rear_indicators"]:
                found_count["rear_indicators"] = all_angle[key]["indicator"]
                if found_count["rear_indicators"] >= 2:
                    if "rear_indicators" in missing:
                        del missing["rear_indicators"]
    if found_count["rear_indicators"] < 2:
        missing["rear_indicators"] = 2 - found_count["rear_indicators"]

    print(found_count)
    print("missing", missing)

    msg = ""
    for key, val in missing.items():
        msg += " " + str(val) + " " + str(key) + " " + "missing" + ","
    msg = msg.strip(",").strip()
    return msg, found_count, missing


def get_missing_response_car(guideline, res_count, lead_id, _lead):
    if res_count["right_side_wheel"] > 2:
        res_count["right_side_wheel"] = 2
    if res_count["hl"] > 2:
        res_count["hl"] = 2
    if res_count["left_side_wheel"] > 2:
        res_count["left_side_wheel"] = 2

    if res_count["f_bumper"] > 1:
        res_count["f_bumper"] = 1
    if res_count["tail_lamp"] > 2:
        res_count["tail_lamp"] = 2
    if res_count["rear_bumper"] > 1:
        res_count["rear_bumper"] = 1
    if res_count["rsv"] > 1:
        res_count["rsv"] = 1
    if res_count["lsv"] > 1:
        res_count["lsv"] = 1

    if guideline["Side_view"]["IsActive"] == "True":
        print("Enter side view")
        _lead["output_data"]["Missing_part_model"]["missing_details"]["Side_view"]["IsActive"] = "True"
        if res_count["lsv"] + res_count["rsv"] < guideline["Side_view"]["Allowed"]:
            _lead["output_data"]["Missing_part_model"]["missing_details"]["Side_view"]["result"] = "Missing"
            _lead["output_data"]["Missing_part_model"]["missing_details"]["Side_view"]["remark"] = \
                guideline["Side_view"]["Remark"]

            if guideline["Side_view"]["Hold_type"] == "Hold-Minor":
                if _lead["QC_status"] != "Rejected":
                    _lead["QC_status"] = "Hold"
                _lead["output_data"]["Missing_part_model"]["missing_details"]["Side_view"]["Model_qc"] = "Hold"
            if guideline["Side_view"]["Hold_type"] == "Hold-Major":
                _lead["QC_status"] = "Rejected"
                _lead["output_data"]["Missing_part_model"]["missing_details"]["Side_view"]["Model_qc"] = "Rejected"

    if guideline["Wheels"]["IsActive"] == "True":
        print("Enter wheel view")
        _lead["output_data"]["Missing_part_model"]["missing_details"]["Wheels"]["IsActive"] = "True"
        if res_count["right_side_wheel"] + res_count["left_side_wheel"] < guideline["Wheels"]["Allowed"]:
            _lead["output_data"]["Missing_part_model"]["missing_details"]["Wheels"]["result"] = "Missing"
            _lead["output_data"]["Missing_part_model"]["missing_details"]["Wheels"]["remark"] = guideline["Wheels"][
                "Remark"]
            if guideline["Wheels"]["Hold_type"] == "Hold-Minor":
                if _lead["QC_status"] != "Rejected":
                    _lead["QC_status"] = "Hold"
                _lead["output_data"]["Missing_part_model"]["missing_details"]["Wheels"]["Model_qc"] = "Hold"
            if guideline["Wheels"]["Hold_type"] == "Hold-Major":
                _lead["QC_status"] = "Rejected"
                _lead["output_data"]["Missing_part_model"]["missing_details"]["Wheels"]["Model_qc"] = "Rejected"

    if guideline["Wipers"]["IsActive"] == "True":
        print("Enter wipers view")
        _lead["output_data"]["Missing_part_model"]["missing_details"]["Wipers"]["IsActive"] = "True"
        if res_count["wipers"] < guideline["Wipers"]["Allowed"]:
            _lead["output_data"]["Missing_part_model"]["missing_details"]["Wipers"]["result"] = "Missing"
            _lead["output_data"]["Missing_part_model"]["missing_details"]["Wipers"]["remark"] = guideline["Wipers"][
                "Remark"]
            if guideline["Wipers"]["Hold_type"] == "Hold-Minor":
                if _lead["QC_status"] != "Rejected":
                    _lead["QC_status"] = "Hold"
                _lead["output_data"]["Missing_part_model"]["missing_details"]["Wipers"]["Model_qc"] = "Hold"
            if guideline["Wipers"]["Hold_type"] == "Hold-Major":
                _lead["QC_status"] = "Rejected"
                _lead["output_data"]["Missing_part_model"]["missing_details"]["Wipers"]["Model_qc"] = "Rejected"

    if guideline["front_bumper"]["IsActive"] == "True" and guideline["rear_bumper"]["IsActive"] == "True":
        _lead["output_data"]["Missing_part_model"]["missing_details"]["Bumper"]["IsActive"] = "True"
        print("Enter bumper view")
        if res_count["f_bumper"] + res_count["rear_bumper"] < guideline["front_bumper"]["Allowed"] + \
                guideline["rear_bumper"]["Allowed"]:
            _lead["output_data"]["Missing_part_model"]["missing_details"]["Bumper"]["result"] = "Missing"
            _lead["output_data"]["Missing_part_model"]["missing_details"]["Bumper"]["remark"] = \
                guideline["front_bumper"]["Remark"]

            if guideline["front_bumper"]["Hold_type"] == "Hold-Minor":
                if _lead["QC_status"] != "Rejected":
                    _lead["QC_status"] = "Hold"
                _lead["output_data"]["Missing_part_model"]["missing_details"]["Bumper"]["Model_qc"] = "Hold"
            if guideline["front_bumper"]["Hold_type"] == "Hold-Major":
                _lead["QC_status"] = "Rejected"
                _lead["output_data"]["Missing_part_model"]["missing_details"]["Bumper"]["Model_qc"] = "Rejected"

    if guideline["hl"]["IsActive"] == "True":
        _lead["output_data"]["Missing_part_model"]["missing_details"]["Headlights"]["IsActive"] = "True"
        print("Enter headlight view")
        if res_count["hl"] < guideline["hl"]["Allowed"] or res_count["tail_lamp"] < guideline["tl"]["Allowed"]:
            _lead["output_data"]["Missing_part_model"]["missing_details"]["Headlights"]["result"] = "Missing"
            _lead["output_data"]["Missing_part_model"]["missing_details"]["Headlights"]["remark"] = guideline["hl"][
                "Remark"]

            if guideline["hl"]["Hold_type"] == "Hold-Minor":
                if _lead["QC_status"] != "Rejected":
                    _lead["QC_status"] = "Hold"
                _lead["output_data"]["Missing_part_model"]["missing_details"]["Headlights"]["Model_qc"] = "Hold"
            if guideline["hl"]["Hold_type"] == "Hold-Major":
                _lead["QC_status"] = "Rejected"
                _lead["output_data"]["Missing_part_model"]["missing_details"]["Headlights"]["Model_qc"] = "Rejected"
    # save_qc_json(lead_id, _lead)
    # x=load_qc_json(lead_id)
    # print("Loading and showing again")
    # print(x["output_data"]["Missing_part_model"]["missing_details"])
    return _lead


def get_missing_response_two(guideline, res_count, lead_id, _lead):
    if guideline["Side_view"]["IsActive"] == "True":
        print("Enter side view")
        _lead["output_data"]["Missing_part_model"]["missing_details"]["Side_view"]["IsActive"] = "True"
        if res_count["sv"] < guideline["Side_view"]["Allowed"]:
            _lead["output_data"]["Missing_part_model"]["missing_details"]["Side_view"]["result"] = "Missing"
            _lead["output_data"]["Missing_part_model"]["missing_details"]["Side_view"]["remark"] = \
                guideline["Side_view"]["Remark"]

            if guideline["Side_view"]["Hold_type"] == "Hold-Minor":
                if _lead["QC_status"] != "Rejected":
                    _lead["QC_status"] = "Hold"
                _lead["output_data"]["Missing_part_model"]["missing_details"]["Side_view"]["Model_qc"] = "Hold"
            if guideline["Side_view"]["Hold_type"] == "Hold-Major":
                _lead["QC_status"] = "Rejected"
                _lead["output_data"]["Missing_part_model"]["missing_details"]["Side_view"]["Model_qc"] = "Rejected"

    if guideline["Wheels"]["IsActive"] == "True":
        print("Enter wheel view")
        _lead["output_data"]["Missing_part_model"]["missing_details"]["Wheels"]["IsActive"] = "True"
        if res_count["Wheel"] < guideline["Wheels"]["Allowed"]:
            _lead["output_data"]["Missing_part_model"]["missing_details"]["Wheels"]["result"] = "Missing"
            _lead["output_data"]["Missing_part_model"]["missing_details"]["Wheels"]["remark"] = guideline["Wheels"][
                "Remark"]
            if guideline["Wheels"]["Hold_type"] == "Hold-Minor":
                if _lead["QC_status"] != "Rejected":
                    _lead["QC_status"] = "Hold"
                _lead["output_data"]["Missing_part_model"]["missing_details"]["Wheels"]["Model_qc"] = "Hold"
            if guideline["Wheels"]["Hold_type"] == "Hold-Major":
                _lead["QC_status"] = "Rejected"
                _lead["output_data"]["Missing_part_model"]["missing_details"]["Wheels"]["Model_qc"] = "Rejected"

    if guideline["Seat"]["IsActive"] == "True":
        print("Enter seat view")
        _lead["output_data"]["Missing_part_model"]["missing_details"]["Seat"]["IsActive"] = "True"
        if res_count["seat"] < guideline["Seat"]["Allowed"]:
            _lead["output_data"]["Missing_part_model"]["missing_details"]["Seat"]["result"] = "Missing"
            _lead["output_data"]["Missing_part_model"]["missing_details"]["Seat"]["remark"] = guideline["Seat"][
                "Remark"]

            if guideline["Seat"]["Hold_type"] == "Hold-Minor":
                if _lead["QC_status"] != "Rejected":
                    _lead["QC_status"] = "Hold"
                _lead["output_data"]["Missing_part_model"]["missing_details"]["Seat"]["Model_qc"] = "Hold"
            if guideline["Seat"]["Hold_type"] == "Hold-Major":
                _lead["QC_status"] = "Rejected"
                _lead["output_data"]["Missing_part_model"]["missing_details"]["Seat"]["Model_qc"] = "Rejected"

    if guideline["Silencer"]["IsActive"] == "True":
        print("Enter wipers view")
        _lead["output_data"]["Missing_part_model"]["missing_details"]["Silencer"]["IsActive"] = "True"
        if res_count["sil"] < guideline["Silencer"]["Allowed"]:
            _lead["output_data"]["Missing_part_model"]["missing_details"]["Silencer"]["result"] = "Missing"
            _lead["output_data"]["Missing_part_model"]["missing_details"]["Silencer"]["remark"] = guideline["Silencer"][
                "Remark"]

            if guideline["Silencer"]["Hold_type"] == "Hold-Minor":
                if _lead["QC_status"] != "Rejected":
                    _lead["QC_status"] = "Hold"
                _lead["output_data"]["Missing_part_model"]["missing_details"]["Silencer"]["Model_qc"] = "Hold"
            if guideline["Silencer"]["Hold_type"] == "Hold-Major":
                _lead["QC_status"] = "Rejected"
                _lead["output_data"]["Missing_part_model"]["missing_details"]["Silencer"]["Model_qc"] = "Rejected"

    if guideline["hl"]["IsActive"] == "True":
        _lead["output_data"]["Missing_part_model"]["missing_details"]["Headlights"]["IsActive"] = "True"
        print("Enter headlight view")
        if res_count["hl"] + res_count["front_indicators"] < guideline["hl"]["Allowed"] or res_count["tl"] + res_count[
            "rear_indicators"] < guideline["tl"]["Allowed"]:
            _lead["output_data"]["Missing_part_model"]["missing_details"]["Headlights"]["result"] = "Missing"
            _lead["output_data"]["Missing_part_model"]["missing_details"]["Headlights"]["remark"] = guideline["hl"][
                "Remark"]

            if guideline["hl"]["Hold_type"] == "Hold-Minor":
                if _lead["QC_status"] != "Rejected":
                    _lead["QC_status"] = "Hold"
                _lead["output_data"]["Missing_part_model"]["missing_details"]["Headlights"]["Model_qc"] = "Hold"
            if guideline["hl"]["Hold_type"] == "Hold-Major":
                _lead["QC_status"] = "Rejected"
                _lead["output_data"]["Missing_part_model"]["missing_details"]["Headlights"]["Model_qc"] = "Rejected"

    # del _lead["output_data"]["Missing_part_model"]["missing_details"]["Bumper"]
    # del _lead["output_data"]["Missing_part_model"]["missing_details"]["Wipers"]
    # print(_lead["output_data"]["Missing_part_model"]["missing_details"])
    # save_qc_json(lead_id, _lead)
    return _lead


def send_qc_response(lead_id):
    _lead = load_vahan_qc_json(lead_id)
    # url = "https://dev.checkexplore.com/VCWebAPI/api/AI/AIQCStaus"
    url="https://oriental.vahancheck.com/VCWebAPI/api/AI/AIQCStaus"
    #url = response_url
    a = requests.post(url, json=_lead)
    print("The status code is", a.status_code)


response_str = {
    "LeadId": "1072267",
    "AIQCStatus": "Rejected",
    "AIQCRemark": "Rejected Registration Number Miss Matched with RC Book Reg.No.",
    "LeadInsepctionAIOutput": [{
        "AI_Model": "RC_Model",
        "AI_SubModel": "Customer First Name with RC Book (Matched with Input Parameter)",
        "PartName": "",
        "model_status": False,
        "model_result": "",
        "Match_Result": False,
        "Remark": "String",
        "Processing_Time": 0.00000,
        "Remarks": "",
        "AIModelResultPercentage": "100%",
        "HoldTypeWheightage": "Hold-Minor",
        "AIQCStatus": "Approve",
        "NoOfDamageCount": "",
        "Video_Remarks": "NA",
        "Video_AIModelResultPercentage": "100%",
        "Video_AIQCStatus": "",
        "Video_NoOfDamageCount": ""

    }, {
        "AI_Model": "RC_Model",
        "AI_SubModel": "Customer Last Name with RC Book (Matched with Input Parameter)",
        "PartName": "",
        "model_status": False,
        "model_result": "",
        "Match_Result": False,
        "Remark": "String",
        "Processing_Time": 0.00000,
        "Remarks": "",
        "AIModelResultPercentage": "99.99%",
        "HoldTypeWheightage": "Hold-Minor",
        "AIQCStatus": "Approve",
        "NoOfDamageCount": "",
        "Video_Remarks": "NA",
        "Video_AIModelResultPercentage": "99.99%",
        "Video_AIQCStatus": "",
        "Video_NoOfDamageCount": ""
    }, {
        "AI_Model": "RC_Model",
        "AI_SubModel": "Registration Number with RC Book (Matched with Input Parameter)",
        "PartName": "",
        "model_status": False,
        "model_result": "",
        "Match_Result": False,
        "Remark": "String",
        "Processing_Time": 0.00000,
        "Remarks": "",
        "AIModelResultPercentage": "100%",
        "HoldTypeWheightage": "Hold-Major",
        "AIQCStatus": "Reject",
        "NoOfDamageCount": "",
        "Video_Remarks": "NA",
        "Video_AIModelResultPercentage": "100%",
        "Video_AIQCStatus": "",
        "Video_NoOfDamageCount": ""
    }, {
        "AI_Model": "Registration_Model",
        "AI_SubModel": "Registration Number with Reg. image (Matched with Input Parameter)",
        "PartName": "",
        "model_status": False,
        "model_result": "",
        "Match_Result": False,
        "Remark": "String",
        "Processing_Time": 0.00000,
        "Remarks": "",
        "AIModelResultPercentage": "100%",
        "HoldTypeWheightage": "Hold-Minor",
        "AIQCStatus": "Approve",
        "NoOfDamageCount": "",
        "Video_Remarks": "NA",
        "Video_AIModelResultPercentage": "100%",
        "Video_AIQCStatus": "",
        "Video_NoOfDamageCount": ""
    }, {
        "AI_Model": "Engine_Model",
        "AI_SubModel": "Engine Number (Matched with Input Parameter)",
        "PartName": "",
        "model_status": False,
        "model_result": "",
        "Match_Result": False,
        "Remark": "String",
        "Processing_Time": 0.00000,
        "Remarks": "",
        "AIModelResultPercentage": "100%",
        "HoldTypeWheightage": "Hold-Major",
        "AIQCStatus": "Reject",
        "NoOfDamageCount": "",
        "Video_Remarks": "NA",
        "Video_AIModelResultPercentage": "100%",
        "Video_AIQCStatus": "",
        "Video_NoOfDamageCount": ""
    }, {
        "AI_Model": "Chassis_Model",
        "AI_SubModel": "Chassis Number (Matched with Input Parameter)",
        "PartName": "",
        "model_status": False,
        "model_result": "",
        "Match_Result": False,
        "Remark": "String",
        "Processing_Time": 0.00000,
        "Remarks": "",
        "AIModelResultPercentage": "100%",
        "HoldTypeWheightage": "Hold-Minor",
        "AIQCStatus": "Approve",
        "NoOfDamageCount": "",
        "Video_Remarks": "NA",
        "Video_AIModelResultPercentage": "100%",
        "Video_AIQCStatus": "",
        "Video_NoOfDamageCount": ""
    }, {
        "AI_Model": "RC_Model",
        "AI_SubModel": "Registration Number with Reg. image (Matched with RC Book Reg.No.)",
        "PartName": "",
        "model_status": False,
        "model_result": "",
        "Match_Result": False,
        "Remark": "String",
        "Processing_Time": 0.00000,
        "Remarks": "",
        "AIModelResultPercentage": "100%",
        "HoldTypeWheightage": "Hold-Major",
        "AIQCStatus": "Reject",
        "NoOfDamageCount": "",
        "Video_Remarks": "NA",
        "Video_AIModelResultPercentage": "100%",
        "Video_AIQCStatus": "",
        "Video_NoOfDamageCount": ""
    }, {
        "AI_Model": "RC_Model",
        "AI_SubModel": "Engine Number img (Matched with RC Book Engine.No.)",
        "PartName": "",
        "model_status": False,
        "model_result": "",
        "Match_Result": False,
        "Remark": "String",
        "Processing_Time": 0.00000,
        "Remarks": "",
        "AIModelResultPercentage": "100%",
        "HoldTypeWheightage": "Hold-Major",
        "AIQCStatus": "Reject",
        "NoOfDamageCount": "",
        "Video_Remarks": "NA",
        "Video_AIModelResultPercentage": "100%",
        "Video_AIQCStatus": "",
        "Video_NoOfDamageCount": ""
    }, {
        "AI_Model": "RC_Model",
        "AI_SubModel": "Chassis Number img (Matched with RC Book Chassis No.)",
        "PartName": "",
        "model_status": False,
        "model_result": "",
        "Match_Result": False,
        "Remark": "String",
        "Processing_Time": 0.00000,
        "Remarks": "",
        "AIModelResultPercentage": "100%",
        "HoldTypeWheightage": "Hold-Major",
        "AIQCStatus": "Reject",
        "NoOfDamageCount": "",
        "Video_Remarks": "NA",
        "Video_AIModelResultPercentage": "100%",
        "Video_AIQCStatus": "",
        "Video_NoOfDamageCount": ""
    }, {
        "AI_Model": "Odometer_Model",
        "AI_SubModel": "ODO Meter (Matched with Input Parameter)",
        "PartName": "",
        "model_status": False,
        "model_result": "",
        "Match_Result": False,
        "Remark": "String",
        "Processing_Time": 0.00000,
        "Remarks": "",
        "AIModelResultPercentage": "100%",
        "HoldTypeWheightage": "Hold-Minor",
        "AIQCStatus": "Approve",
        "NoOfDamageCount": "",
        "Video_Remarks": "NA",
        "Video_AIModelResultPercentage": "100%",
        "Video_AIQCStatus": "",
        "Video_NoOfDamageCount": ""
    }, {
        "AI_Model": "RC_Model",
        "AI_SubModel": "RC Book image not available",
        "PartName": "",
        "model_status": False,
        "model_result": "",
        "Match_Result": False,
        "Remark": "String",
        "Processing_Time": 0.00000,
        "Remarks": "",
        "AIModelResultPercentage": "0%",
        "HoldTypeWheightage": "Hold-Minor",
        "AIQCStatus": "Approve",
        "NoOfDamageCount": "",
        "Video_Remarks": "NA",
        "Video_AIModelResultPercentage": "0%",
        "Video_AIQCStatus": "",
        "Video_NoOfDamageCount": ""
    }, {
        "AI_Model": "RC_Model",
        "AI_SubModel": "RC Book image not clear",
        "PartName": "",
        "model_status": False,
        "model_result": "",
        "Match_Result": False,
        "Remark": "String",
        "Processing_Time": 0.00000,
        "Remarks": "",
        "AIModelResultPercentage": "0%",
        "HoldTypeWheightage": "Hold-Minor",
        "AIQCStatus": "Approve",
        "NoOfDamageCount": "",
        "Video_Remarks": "NA",
        "Video_AIModelResultPercentage": "0%",
        "Video_AIQCStatus": "",
        "Video_NoOfDamageCount": ""
    }, {
        "AI_Model": "RPM_Model",
        "AI_SubModel": "RPM ON/OFF",
        "PartName": "",
        "model_status": False,
        "model_result": "",
        "Match_Result": False,
        "Remark": "String",
        "Processing_Time": 0.00000,
        "Remarks": "",
        "AIModelResultPercentage": "0%",
        "HoldTypeWheightage": "Hold-Minor",
        "AIQCStatus": "Approve",
        "NoOfDamageCount": "",
        "Video_Remarks": "NA",
        "Video_AIModelResultPercentage": "0%",
        "Video_AIQCStatus": "",
        "Video_NoOfDamageCount": ""
    }, {
        "AI_Model": "CNG_Model",
        "AI_SubModel": "CNG fitted but not endorsed in RC and vice versa",
        "PartName": "",
        "model_status": False,
        "model_result": "",
        "Match_Result": False,
        "Remark": "String",
        "Processing_Time": 0.00000,
        "Remarks": "",
        "AIModelResultPercentage": "0%",
        "HoldTypeWheightage": "Hold-Minor",
        "AIQCStatus": "Approve",
        "NoOfDamageCount": "",
        "Video_Remarks": "NA",
        "Video_AIModelResultPercentage": "0%",
        "Video_AIQCStatus": "",
        "Video_NoOfDamageCount": ""
    }, {
        "AI_Model": "Garage_Model",
        "AI_SubModel": "Vehicle at Garage",
        "PartName": "",
        "model_status": False,
        "model_result": "",
        "Match_Result": False,
        "Remark": "String",
        "Processing_Time": 0.00000,
        "Remarks": "",
        "AIModelResultPercentage": "0%",
        "HoldTypeWheightage": "Hold-Minor",
        "AIQCStatus": "Approve",
        "NoOfDamageCount": "",
        "Video_Remarks": "NA",
        "Video_AIModelResultPercentage": "0%",
        "Video_AIQCStatus": "",
        "Video_NoOfDamageCount": ""
    }, {
        "AI_Model": "PoliceStation_Model",
        "AI_SubModel": "Vehicle at Police Station",
        "PartName": "",
        "model_status": False,
        "model_result": "",
        "Match_Result": False,
        "Remark": "String",
        "Processing_Time": 0.00000,
        "Remarks": "",
        "AIModelResultPercentage": "0%",
        "HoldTypeWheightage": "Hold-Minor",
        "AIQCStatus": "Approve",
        "NoOfDamageCount": "",
        "Video_Remarks": "NA",
        "Video_AIModelResultPercentage": "0%",
        "Video_AIQCStatus": "",
        "Video_NoOfDamageCount": ""
    }, {
        "AI_Model": "Missing_OR_Broken_part_model",
        "AI_SubModel": "Side view mirrors",
        "PartName": "",
        "model_status": False,
        "model_result": "",
        "Match_Result": False,
        "Remark": "String",
        "Processing_Time": 0.00000,
        "Remarks": "",
        "AIModelResultPercentage": "1 Count",
        "HoldTypeWheightage": "Hold-Minor",
        "AIQCStatus": "Approve",
        "NoOfDamageCount": "",
        "Video_Remarks": "NA",
        "Video_AIModelResultPercentage": "1 Count",
        "Video_AIQCStatus": "",
        "Video_NoOfDamageCount": ""
    }, {
        "AI_Model": "Missing_part_model",
        "AI_SubModel": "Bumper (front and back)",
        "PartName": "",
        "model_status": False,
        "model_result": "",
        "Match_Result": False,
        "Remark": "String",
        "Processing_Time": 0.00000,
        "Remarks": "",
        "AIModelResultPercentage": "2 Count",
        "HoldTypeWheightage": "Hold-Major",
        "AIQCStatus": "Reject",
        "NoOfDamageCount": "",
        "Video_Remarks": "NA",
        "Video_AIModelResultPercentage": "2 Count",
        "Video_AIQCStatus": "",
        "Video_NoOfDamageCount": ""
    }, {
        "AI_Model": "Missing_part_model",
        "AI_SubModel": "Wipers",
        "PartName": "",
        "model_status": False,
        "model_result": "",
        "Match_Result": False,
        "Remark": "String",
        "Processing_Time": 0.00000,
        "Remarks": "",
        "AIModelResultPercentage": "1 Count",
        "HoldTypeWheightage": "Hold-Minor",
        "AIQCStatus": "Approve",
        "NoOfDamageCount": "",
        "Video_Remarks": "NA",
        "Video_AIModelResultPercentage": "1 Count",
        "Video_AIQCStatus": "",
        "Video_NoOfDamageCount": ""
    }, {
        "AI_Model": "Missing_OR_Broken_part_model",
        "AI_SubModel": "Headlights (front and back) - Head lamp/Tail lamp/Indicators/Fog Lamp (front and back)",
        "PartName": "",
        "model_status": False,
        "model_result": "",
        "Match_Result": False,
        "Remark": "String",
        "Processing_Time": 0.00000,
        "Remarks": "",
        "AIModelResultPercentage": "2 Count",
        "HoldTypeWheightage": "Hold-Major",
        "AIQCStatus": "Reject",
        "NoOfDamageCount": "",
        "Video_Remarks": "NA",
        "Video_AIModelResultPercentage": "2 Count",
        "Video_AIQCStatus": "",
        "Video_NoOfDamageCount": ""
    }, {
        "AI_Model": "Missing_part_model",
        "AI_SubModel": "Wheels (4)",
        "PartName": "",
        "model_status": False,
        "model_result": "",
        "Match_Result": False,
        "Remark": "String",
        "Processing_Time": 0.00000,
        "Remarks": "",
        "AIModelResultPercentage": "4 Count",
        "HoldTypeWheightage": "Hold-Major",
        "AIQCStatus": "Reject",
        "NoOfDamageCount": "",
        "Video_Remarks": "NA",
        "Video_AIModelResultPercentage": "4 Count",
        "Video_AIQCStatus": "",
        "Video_NoOfDamageCount": ""
    }, {
        "AI_Model": "Missing_OR_Broken_part_model",
        "AI_SubModel": "Window glass/ Rear glass (front and back)",
        "PartName": "",
        "model_status": False,
        "model_result": "",
        "Match_Result": False,
        "Remark": "String",
        "Processing_Time": 0.00000,
        "Remarks": "",
        "AIModelResultPercentage": "4 Count",
        "HoldTypeWheightage": "Hold-Minor",
        "AIQCStatus": "Approve",
        "NoOfDamageCount": "",
        "Video_Remarks": "NA",
        "Video_AIModelResultPercentage": "4 Count",
        "Video_AIQCStatus": "",
        "Video_NoOfDamageCount": ""
    }, {
        "AI_Model": "Missing_OR_Broken_part_model",
        "AI_SubModel": "Windshield (front and back)",
        "PartName": "",
        "model_status": False,
        "model_result": "",
        "Match_Result": False,
        "Remark": "String",
        "Processing_Time": 0.00000,
        "Remarks": "",
        "AIModelResultPercentage": "2 Count",
        "HoldTypeWheightage": "Hold-Minor",
        "AIQCStatus": "Approve",
        "NoOfDamageCount": "",
        "Video_Remarks": "NA",
        "Video_AIModelResultPercentage": "2 Count",
        "Video_AIQCStatus": "",
        "Video_NoOfDamageCount": ""
    }, {
        "AI_Model": "Missing_part_model",
        "AI_SubModel": "Hologram/monogram (in the front/back grill) are stolen",
        "PartName": "",
        "model_status": False,
        "model_result": "",
        "Match_Result": False,
        "Remark": "String",
        "Processing_Time": 0.00000,
        "Remarks": "",
        "AIModelResultPercentage": "1 Count",
        "HoldTypeWheightage": "Hold-Minor",
        "AIQCStatus": "Approve",
        "NoOfDamageCount": "",
        "Video_Remarks": "NA",
        "Video_AIModelResultPercentage": "1 Count",
        "Video_AIQCStatus": "",
        "Video_NoOfDamageCount": ""
    }, {
        "AI_Model": "Damage_Model",
        "AI_SubModel": "Front Panel",
        "PartName": "",
        "model_status": False,
        "model_result": "",
        "Match_Result": False,
        "Remark": "String",
        "Processing_Time": 0.00000,
        "Remarks": "",
        "AIModelResultPercentage": "NA",
        "HoldTypeWheightage": "",
        "AIQCStatus": "NA",
        "NoOfDamageCount": "",
        "Video_Remarks": "NA",
        "Video_AIModelResultPercentage": "NA",
        "Video_AIQCStatus": "",
        "Video_NoOfDamageCount": ""
    }, {
        "AI_Model": "Damage_Model",
        "AI_SubModel": "Front Right Side Panel",
        "PartName": "",
        "model_status": False,
        "model_result": "",
        "Match_Result": False,
        "Remark": "String",
        "Processing_Time": 0.00000,
        "Remarks": "",
        "AIModelResultPercentage": "NA",
        "HoldTypeWheightage": "",
        "AIQCStatus": "NA",
        "NoOfDamageCount": "",
        "Video_Remarks": "NA",
        "Video_AIModelResultPercentage": "NA",
        "Video_AIQCStatus": "",
        "Video_NoOfDamageCount": ""
    }, {
        "AI_Model": "Damage_Model",
        "AI_SubModel": "Front Left Side Panel",
        "PartName": "",
        "model_status": False,
        "model_result": "",
        "Match_Result": False,
        "Remark": "String",
        "Processing_Time": 0.00000,
        "Remarks": "",
        "AIModelResultPercentage": "NA",
        "HoldTypeWheightage": "",
        "AIQCStatus": "NA",
        "NoOfDamageCount": "",
        "Video_Remarks": "NA",
        "Video_AIModelResultPercentage": "NA",
        "Video_AIQCStatus": "",
        "Video_NoOfDamageCount": ""
    }, {
        "AI_Model": "Damage_Model",
        "AI_SubModel": "Back Right Side Panel",
        "PartName": "",
        "model_status": False,
        "model_result": "",
        "Match_Result": False,
        "Remark": "String",
        "Processing_Time": 0.00000,
        "Remarks": "",
        "AIModelResultPercentage": "NA",
        "HoldTypeWheightage": "",
        "AIQCStatus": "NA",
        "NoOfDamageCount": "",
        "Video_Remarks": "NA",
        "Video_AIModelResultPercentage": "NA",
        "Video_AIQCStatus": "",
        "Video_NoOfDamageCount": ""
    }, {
        "AI_Model": "Damage_Model",
        "AI_SubModel": "Back Left Side Panel",
        "PartName": "",
        "model_status": False,
        "model_result": "",
        "Match_Result": False,
        "Remark": "String",
        "Processing_Time": 0.00000,
        "Remarks": "",
        "AIModelResultPercentage": "NA",
        "HoldTypeWheightage": "",
        "AIQCStatus": "NA",
        "NoOfDamageCount": "",
        "Video_Remarks": "NA",
        "Video_AIModelResultPercentage": "NA",
        "Video_AIQCStatus": "",
        "Video_NoOfDamageCount": ""
    }, {
        "AI_Model": "Damage_Model",
        "AI_SubModel": "Back Panel",
        "PartName": "",
        "model_status": False,
        "model_result": "",
        "Match_Result": False,
        "Remark": "String",
        "Processing_Time": 0.00000,
        "Remarks": "",
        "AIModelResultPercentage": "NA",
        "HoldTypeWheightage": "",
        "AIQCStatus": "NA",
        "NoOfDamageCount": "",
        "Video_Remarks": "NA",
        "Video_AIModelResultPercentage": "NA",
        "Video_AIQCStatus": "",
        "Video_NoOfDamageCount": ""
    }, {
        "AI_Model": "Damage_Model",
        "AI_SubModel": "All Panel",
        "PartName": "",
        "model_status": False,
        "model_result": "",
        "Match_Result": False,
        "Remark": "String",
        "Processing_Time": 0.00000,
        "Remarks": "",
        "AIModelResultPercentage": "4 count",
        "HoldTypeWheightage": "Hold-Major",
        "AIQCStatus": "Reject",
        "NoOfDamageCount": "",
        "Video_Remarks": "NA",
        "Video_AIModelResultPercentage": "4 count",
        "Video_AIQCStatus": "",
        "Video_NoOfDamageCount": ""
    }, {
        "AI_Model": "Video_Model",
        "AI_SubModel": "Identify  that Photos and Video is of same vehicle",
        "PartName": "",
        "model_status": False,
        "model_result": "",
        "Match_Result": False,
        "Remark": "String",
        "Processing_Time": 0.00000,
        "Remarks": "",
        "AIModelResultPercentage": "100%",
        "HoldTypeWheightage": "Hold-Major",
        "AIQCStatus": "Reject",
        "NoOfDamageCount": "",
        "Video_Remarks": "NA",
        "Video_AIModelResultPercentage": "100%",
        "Video_AIQCStatus": "",
        "Video_NoOfDamageCount": ""
    }, {
        "AI_Model": "Video_Model",
        "AI_SubModel": "Vehicle is started (Engine ON sound )",
        "PartName": "",
        "model_status": False,
        "model_result": "",
        "Match_Result": False,
        "Remark": "String",
        "Processing_Time": 0.00000,
        "Remarks": "",
        "AIModelResultPercentage": "50%",
        "HoldTypeWheightage": "Hold-Minor",
        "AIQCStatus": "Approve",
        "NoOfDamageCount": "",
        "Video_Remarks": "NA",
        "Video_AIModelResultPercentage": "50%",
        "Video_AIQCStatus": "",
        "Video_NoOfDamageCount": ""
    }, {
        "AI_Model": "Video_Model",
        "AI_SubModel": "Proper 360 deg view, No Video frame change, no stop between, continous video shoot",
        "PartName": "",
        "model_status": False,
        "model_result": "",
        "Match_Result": False,
        "Remark": "String",
        "Processing_Time": 0.00000,
        "Remarks": "",
        "AIModelResultPercentage": "100%",
        "HoldTypeWheightage": "Hold-Major",
        "AIQCStatus": "Reject",
        "NoOfDamageCount": "",
        "Video_Remarks": "NA",
        "Video_AIModelResultPercentage": "100%",
        "Video_AIQCStatus": "",
        "Video_NoOfDamageCount": ""
    }, {
        "AI_Model": "Video_Model",
        "AI_SubModel": "No external object in between, like pole, wall, other vehicle, person standing",
        "PartName": "",
        "model_status": False,
        "model_result": "",
        "Match_Result": False,
        "Remark": "String",
        "Processing_Time": 0.00000,
        "Remarks": "",
        "AIModelResultPercentage": "50%",
        "HoldTypeWheightage": "Hold-Minor",
        "AIQCStatus": "Approve",
        "NoOfDamageCount": "",
        "Video_Remarks": "NA",
        "Video_AIModelResultPercentage": "50%",
        "Video_AIQCStatus": "",
        "Video_NoOfDamageCount": ""
    }, {
        "AI_Model": "VehicleMismatch_Model",
        "AI_SubModel": "Vehicle Type Mismatch",
        "PartName": "",
        "model_status": False,
        "model_result": "",
        "Match_Result": False,
        "Remark": "String",
        "Processing_Time": 0.00000,
        "Remarks": "",
        "AIModelResultPercentage": "100%",
        "HoldTypeWheightage": "Hold-Minor",
        "AIQCStatus": "Approve",
        "NoOfDamageCount": "",
        "Video_Remarks": "NA",
        "Video_AIModelResultPercentage": "100%",
        "Video_AIQCStatus": "",
        "Video_NoOfDamageCount": ""
    }
    ]
}


def upload_to_ftp(lead_id):
    bashCommand = f"ncftpput -u ai -p Avce@123 -R 169.38.102.61 {lead_id}/ {lead_id}/AI"
    process = subprocess.Popen(bashCommand, shell=True)
    
    


# Final check function statement
def final_check(data):
    indexes = []
    for i in range(len(data['LeadInsepctionAIOutput'])):
        if data['LeadInsepctionAIOutput'][i]['model_status'] == 'False' or data['LeadInsepctionAIOutput'][i][
            'model_status'] == False:
            indexes.append(i)

    # print(indexes)
    # deleting the indexes before saving it as a json file
    for index in sorted(indexes, reverse=True):
        del data['LeadInsepctionAIOutput'][index]

    return data


def final_processing(lead_id):
    new = copy.deepcopy(response_str)
    # with open("default_new.json", "r") as read_file:
    #     new = json.load(read_file)

    data = load_qc_json(lead_id)

    source = f"{lead_id}/QC_Result.json"
    destination = f"{lead_id}/Processed/internal.pkl"
    # shutil.move(source, destination) 

    # os.remove(source)

    with open(destination, 'wb') as handle:
        pickle.dump(data, handle)

    time_source = f"{lead_id}/processing_time.json"

    if path.exists(time_source):
        time_destination = f"{lead_id}/Processed/Processing_time.json"
        shutil.move(time_source, time_destination)

    if "front" not in data['output_data']['DND']['panel_wise']:
        data['output_data']['DND']['panel_wise']["front"] = 0
    if "front_left" not in data['output_data']['DND']['panel_wise']:
        data['output_data']['DND']['panel_wise']["front_left"] = 0
    if "front_right" not in data['output_data']['DND']['panel_wise']:
        data['output_data']['DND']['panel_wise']["front_right"] = 0
    if "rear_right" not in data['output_data']['DND']['panel_wise']:
        data['output_data']['DND']['panel_wise']["rear_right"] = 0
    if "rear_left" not in data['output_data']['DND']['panel_wise']:
        data['output_data']['DND']['panel_wise']["rear_left"] = 0
    if "rear" not in data['output_data']['DND']['panel_wise']:
        data['output_data']['DND']['panel_wise']["rear"] = 0
    if "right" not in data['output_data']['DND']['panel_wise']:
        data['output_data']['DND']['panel_wise']["right"] = 0
    if "left" not in data['output_data']['DND']['panel_wise']:
        data['output_data']['DND']['panel_wise']["left"] = 0

    new['LeadId'] = data['leadId']
    new['AIQCStatus'] = data['QC_status']
    new['AIQCRemark'] = data['QC_remarks']

    # RC model
    # First Name
    new['LeadInsepctionAIOutput'][0]['AI_Model'] = 'RC_Model'
    new['LeadInsepctionAIOutput'][0]['AI_SubModel'] = 'Customer First Name with RC Book (Matched with Input Parameter) '
    new['LeadInsepctionAIOutput'][0]['PartName'] = ''
    new['LeadInsepctionAIOutput'][0]['model_status'] = data['output_data']['RC_Model']['First_name']['Is_Active']
    new['LeadInsepctionAIOutput'][0]['model_result'] = data['output_data']['RC_Model']['First_name']['model_result']
    if data['output_data']['RC_Model']['First_name']['First_name_matches_with_input'] == 'Matched':
        new['LeadInsepctionAIOutput'][0]['Match_Result'] = True
    else:
        new['LeadInsepctionAIOutput'][0]['Match_Result'] = False
    new['LeadInsepctionAIOutput'][0]['Remark'] = data['output_data']['RC_Model']['First_name']['Remark']
    new['LeadInsepctionAIOutput'][0]['Processing_Time'] = data['output_data']['RC_Model']['Processing Time']
    # new['LeadInsepctionAIOutput'][0]['AIQCStatus'] = data['QC_status']
    new['LeadInsepctionAIOutput'][0]['AIQCStatus'] = data['output_data']['RC_Model']['First_name']['Model_qc']

    # Last Name
    new['LeadInsepctionAIOutput'][1]['AI_Model'] = 'RC_Model'
    new['LeadInsepctionAIOutput'][1]['AI_SubModel'] = 'Customer Last Name with RC Book (Matched with Input Parameter) '
    new['LeadInsepctionAIOutput'][1]['PartName'] = ''
    new['LeadInsepctionAIOutput'][1]['model_status'] = data['output_data']['RC_Model']['Last_name']['Is_Active']
    new['LeadInsepctionAIOutput'][1]['model_result'] = data['output_data']['RC_Model']['Last_name']['model_result']
    if data['output_data']['RC_Model']['Last_name']['Last_name_matches_with_input'] == 'Matched':
        new['LeadInsepctionAIOutput'][1]['Match_Result'] = True
    else:
        new['LeadInsepctionAIOutput'][1]['Match_Result'] = False
    new['LeadInsepctionAIOutput'][1]['Remark'] = data['output_data']['RC_Model']['Last_name']['Remark']
    new['LeadInsepctionAIOutput'][1]['Processing_Time'] = data['output_data']['RC_Model']['Processing Time']
    # new['LeadInsepctionAIOutput'][1]['AIQCStatus'] = data['QC_status']
    new['LeadInsepctionAIOutput'][1]['AIQCStatus'] = data['output_data']['RC_Model']['Last_name']['Model_qc']

    # Registration
    new['LeadInsepctionAIOutput'][2]['AI_Model'] = 'RC_Model'
    new['LeadInsepctionAIOutput'][2]['AI_SubModel'] = 'Registration Number with RC Book (Matched with Input Parameter)'
    new['LeadInsepctionAIOutput'][2]['PartName'] = ''
    new['LeadInsepctionAIOutput'][2]['model_status'] = data['output_data']['RC_Model']['Registration']['Is_Active']
    new['LeadInsepctionAIOutput'][2]['model_result'] = data['output_data']['RC_Model']['Registration']['model_result']
    new['LeadInsepctionAIOutput'][2]['Match_Result'] = data['output_data']['RC_Model']['Registration'][
        'Registration_Number_matches_with_input']
    new['LeadInsepctionAIOutput'][2]['Remark'] = data['output_data']['RC_Model']['Registration']['Remark']
    new['LeadInsepctionAIOutput'][2]['Processing_Time'] = data['output_data']['RC_Model']['Processing Time']
    # new['LeadInsepctionAIOutput'][2]['AIQCStatus'] = data['QC_status']
    new['LeadInsepctionAIOutput'][2]['AIQCStatus'] = data['output_data']['RC_Model']['Registration']['Model_qc']

    #######################################################################################################################
    # Number plate model
    new['LeadInsepctionAIOutput'][3]['AI_Model'] = 'Registration_Model'
    new['LeadInsepctionAIOutput'][3][
        'AI_SubModel'] = 'Registration Number with Reg. image (Matched with Input Parameter)'
    new['LeadInsepctionAIOutput'][3]['PartName'] = ''
    new['LeadInsepctionAIOutput'][3]['model_status'] = data['output_data']['Number_Plate_Model']['Is_Active']
    new['LeadInsepctionAIOutput'][3]['model_result'] = data['output_data']['Number_Plate_Model']['model_result']
    new['LeadInsepctionAIOutput'][3]['Match_Result'] = data['output_data']['Number_Plate_Model'][
        'Number_plate_matches_with_input']
    new['LeadInsepctionAIOutput'][3]['Remark'] = data['output_data']['Number_Plate_Model']['Remark']
    new['LeadInsepctionAIOutput'][3]['Processing_Time'] = data['output_data']['Number_Plate_Model']['Processing Time']
    # new['LeadInsepctionAIOutput'][3]['AIQCStatus'] = data['QC_status']
    new['LeadInsepctionAIOutput'][3]['AIQCStatus'] = data['output_data']['Number_Plate_Model']['Model_qc']
    new['LeadInsepctionAIOutput'][3]['Video_AIQCStatus'] = data["output_data"]["Number_Plate_Model"]["Video_AIQCStatus"]
    new['LeadInsepctionAIOutput'][3]['Video_Remarks'] = data["output_data"]["Number_Plate_Model"]["Video_Remarks"]
    #######################################################################################################################

    # Chassis Model
    new['LeadInsepctionAIOutput'][5]['AI_Model'] = 'Chassis_Model'
    new['LeadInsepctionAIOutput'][5]['AI_SubModel'] = ''
    new['LeadInsepctionAIOutput'][5]['PartName'] = ''
    new['LeadInsepctionAIOutput'][5]['model_status'] = data['output_data']['Chassis_model']['Is_Active']
    new['LeadInsepctionAIOutput'][5]['model_result'] = data['output_data']['Chassis_model']['model_result']
    new['LeadInsepctionAIOutput'][5]['Match_Result'] = data['output_data']['Chassis_model'][
        'Chassis_Number_matches_with_input']
    new['LeadInsepctionAIOutput'][5]['Remark'] = data['output_data']['Chassis_model']['Remark']
    new['LeadInsepctionAIOutput'][5]['Processing_Time'] = data['output_data']['Chassis_model']['Processing Time']
    # new['LeadInsepctionAIOutput'][5]['AIQCStatus'] = data['QC_status']
    new['LeadInsepctionAIOutput'][5]['AIQCStatus'] = data['output_data']['Chassis_model']['Model_qc']
    new['LeadInsepctionAIOutput'][5]['Video_AIQCStatus'] = data["output_data"]["Chassis_model"]["Video_AIQCStatus"]
    new['LeadInsepctionAIOutput'][5]['Video_Remarks'] = data["output_data"]["Chassis_model"]["Video_Remarks"]
    #####################################################################################################################
    # RC_model ,engine
    new['LeadInsepctionAIOutput'][7]['AI_Model'] = 'RC_Model'
    new['LeadInsepctionAIOutput'][7]['AI_SubModel'] = 'Engine Number img (Matched with RC Book Engine.No.) '
    new['LeadInsepctionAIOutput'][7]['PartName'] = ''
    new['LeadInsepctionAIOutput'][7]['model_status'] = data['output_data']['RC_Model']['Engine']['Is_Active']
    new['LeadInsepctionAIOutput'][7]['model_result'] = data['output_data']['RC_Model']['Engine']['model_result']
    new['LeadInsepctionAIOutput'][7]['Match_Result'] = data['output_data']['RC_Model']['Engine'][
        'Engine_Number_matches_with_input']
    new['LeadInsepctionAIOutput'][7]['Remark'] = data['output_data']['RC_Model']['Engine']['Remark']
    new['LeadInsepctionAIOutput'][7]['Processing_Time'] = data['output_data']['RC_Model']['Processing Time']
    new['LeadInsepctionAIOutput'][7]['AIQCStatus'] = data['output_data']['RC_Model']['Engine']['Model_qc']

    # RC_model, Chassis
    new['LeadInsepctionAIOutput'][8]['AI_Model'] = 'RC_Model'
    new['LeadInsepctionAIOutput'][8]['AI_SubModel'] = 'Chassis Number img (Matched with RC Book Chassis No.) '
    new['LeadInsepctionAIOutput'][8]['PartName'] = ''
    new['LeadInsepctionAIOutput'][8]['model_status'] = data['output_data']['RC_Model']['Chassis']['Is_Active']
    new['LeadInsepctionAIOutput'][8]['model_result'] = data['output_data']['RC_Model']['Chassis']['model_result']
    new['LeadInsepctionAIOutput'][8]['Match_Result'] = data['output_data']['RC_Model']['Chassis'][
        'Chassis_Number_matches_with_input']
    new['LeadInsepctionAIOutput'][8]['Remark'] = data['output_data']['RC_Model']['Chassis']['Remark']
    new['LeadInsepctionAIOutput'][8]['Processing_Time'] = data['output_data']['RC_Model']['Processing Time']
    new['LeadInsepctionAIOutput'][8]['AIQCStatus'] = data['output_data']['RC_Model']['Chassis']['Model_qc']
    ####################################################################################################################
    # Odometer model
    new['LeadInsepctionAIOutput'][9]['AI_Model'] = 'Odometer_Model'
    new['LeadInsepctionAIOutput'][9]['AI_SubModel'] = 'ODO Meter (Matched with Input Parameter)'
    new['LeadInsepctionAIOutput'][9]['PartName'] = ''
    new['LeadInsepctionAIOutput'][9]['model_status'] = data['output_data']['Odometer_Model']['Is_Active']
    new['LeadInsepctionAIOutput'][9]['model_result'] = data['output_data']['Odometer_Model']['model_result']
    new['LeadInsepctionAIOutput'][9]['Match_Result'] = data['output_data']['Odometer_Model'][
        'Odometer_matches_with_input']
    new['LeadInsepctionAIOutput'][9]['Remark'] = data['output_data']['Odometer_Model']['Remark']
    new['LeadInsepctionAIOutput'][9]['Processing_Time'] = data['output_data']['Odometer_Model']['Processing Time']
    new['LeadInsepctionAIOutput'][9]['AIQCStatus'] = data['output_data']['Odometer_Model']['Model_qc']
    new['LeadInsepctionAIOutput'][9]['Video_AIQCStatus'] = data["output_data"]["Odometer_Model"]["Video_AIQCStatus"]
    new['LeadInsepctionAIOutput'][9]['Video_Remarks'] = data["output_data"]["Odometer_Model"]["Video_Remarks"]

    # RC_availability
    new['LeadInsepctionAIOutput'][10]['AI_Model'] = 'RC_Model'
    new['LeadInsepctionAIOutput'][10]['AI_SubModel'] = 'RC Book image not available'
    new['LeadInsepctionAIOutput'][10]['PartName'] = ''
    new['LeadInsepctionAIOutput'][10]['model_status'] = data['output_data']['RC_Model']['RC_availability'][
        'Is_Active']
    new['LeadInsepctionAIOutput'][10]['model_result'] = data['output_data']['RC_Model']['RC_availability'][
        'model_result']
    new['LeadInsepctionAIOutput'][10]['Remark'] = data['output_data']['RC_Model']['RC_availability']['Remark']
    new['LeadInsepctionAIOutput'][10]['Processing_Time'] = data['output_data']['RC_Model']['Processing Time']
    new['LeadInsepctionAIOutput'][10]['AIQCStatus'] = data['output_data']['RC_Model']['RC_availability']['Model_qc']

    # RPM model
    new['LeadInsepctionAIOutput'][12]['AI_Model'] = 'Rpm_Model'
    new['LeadInsepctionAIOutput'][12]['AI_SubModel'] = 'RPM ON/OFF'
    new['LeadInsepctionAIOutput'][12]['PartName'] = ''
    new['LeadInsepctionAIOutput'][12]['model_status'] = data['output_data']['Rpm_Model']['Is_Active']
    new['LeadInsepctionAIOutput'][12]['model_result'] = data['output_data']['Rpm_Model']['model_result']
    new['LeadInsepctionAIOutput'][12]['Remark'] = data['output_data']['Rpm_Model']['needle_reading']
    new['LeadInsepctionAIOutput'][12]['Processing_Time'] = data['output_data']['Rpm_Model']['Processing Time']
    new['LeadInsepctionAIOutput'][12]['AIQCStatus'] = data['output_data']['Rpm_Model']['Model_qc']

    # CNG model
    new['LeadInsepctionAIOutput'][13]['AI_Model'] = 'CNG_Model'
    new['LeadInsepctionAIOutput'][13]['AI_SubModel'] = 'CNG fitted but not endorsed in RC and vice versa'
    new['LeadInsepctionAIOutput'][13]['PartName'] = ''
    new['LeadInsepctionAIOutput'][13]['model_status'] = data['output_data']['RC_Model']['CNG']['Is_Active']
    new['LeadInsepctionAIOutput'][13]['model_result'] = data['output_data']['RC_Model']['CNG']['model_result']
    new['LeadInsepctionAIOutput'][13]['Remark'] = data['output_data']['RC_Model']['CNG']['Remark']
    new['LeadInsepctionAIOutput'][13]['Processing_Time'] = data['output_data']['RC_Model']['Processing Time']
    new['LeadInsepctionAIOutput'][13]['AIQCStatus'] = data['output_data']['RC_Model']['CNG']['Model_qc']

    # Garage Model
    new['LeadInsepctionAIOutput'][14]['AI_Model'] = 'Garage_Model'
    new['LeadInsepctionAIOutput'][14]['AI_SubModel'] = 'Vehicle at Garage'
    new['LeadInsepctionAIOutput'][14]['PartName'] = ''
    new['LeadInsepctionAIOutput'][14]['model_status'] = data['output_data']['Garage_Detection']['Is_Active']
    new['LeadInsepctionAIOutput'][14]['model_result'] = data['output_data']['Garage_Detection']['model_result']
    new['LeadInsepctionAIOutput'][14]['Remark'] = data['output_data']['Garage_Detection']['Remark']
    new['LeadInsepctionAIOutput'][14]['Processing_Time'] = data['output_data']['Garage_Detection']['Processing Time']
    new['LeadInsepctionAIOutput'][14]['AIQCStatus'] = data['output_data']['Garage_Detection']['Model_qc']

    # Police Station Model
    new['LeadInsepctionAIOutput'][15]['AI_Model'] = 'PoliceStation_Model'
    new['LeadInsepctionAIOutput'][15]['AI_SubModel'] = 'Vehicle at Police Station'
    new['LeadInsepctionAIOutput'][15]['PartName'] = ''
    new['LeadInsepctionAIOutput'][15]['model_status'] = data['output_data']['Police_detection']['Is_Active']
    new['LeadInsepctionAIOutput'][15]['model_result'] = data['output_data']['Police_detection']['model_result']
    new['LeadInsepctionAIOutput'][15]['Remark'] = data['output_data']['Police_detection']['Remark']
    new['LeadInsepctionAIOutput'][15]['Processing_Time'] = data['output_data']['Police_detection']['Processing Time']
    new['LeadInsepctionAIOutput'][15]['AIQCStatus'] = data['output_data']['Police_detection']['Model_qc']

    # Missing or Broken Parts model
    # Side View Mirrors
    new['LeadInsepctionAIOutput'][16]['AI_Model'] = 'Missing_part_model'
    new['LeadInsepctionAIOutput'][16]['AI_SubModel'] = 'Side view mirrors'
    new['LeadInsepctionAIOutput'][16]['PartName'] = ''
    new['LeadInsepctionAIOutput'][16]['model_status'] = \
        data['output_data']['Missing_part_model']['missing_details']['Side_view']['IsActive']
    new['LeadInsepctionAIOutput'][16]['model_result'] = \
        data['output_data']['Missing_part_model']['missing_details']['Side_view']['result']
    new['LeadInsepctionAIOutput'][16]['Remark'] = \
        data['output_data']['Missing_part_model']['missing_details']['Side_view']['remark']
    new['LeadInsepctionAIOutput'][16]['Processing_Time'] = data['output_data']['Missing_part_model']['Processing Time']
    new['LeadInsepctionAIOutput'][16]['AIQCStatus'] = \
        data['output_data']['Missing_part_model']['missing_details']['Side_view']['Model_qc']

    # Bumpers (front and back)
    if data["output_data"]["vehicle_type_model"]["model_result"] == "Two wheeler":
        new['LeadInsepctionAIOutput'][17]['AI_Model'] = 'Missing_part_model'
        new['LeadInsepctionAIOutput'][17]['AI_SubModel'] = 'Silencer'
        new['LeadInsepctionAIOutput'][17]['PartName'] = ''
        new['LeadInsepctionAIOutput'][17]['model_status'] = \
            data['output_data']['Missing_part_model']['missing_details']['Silencer']['IsActive']
        new['LeadInsepctionAIOutput'][17]['model_result'] = \
            data['output_data']['Missing_part_model']['missing_details']['Silencer']['result']
        new['LeadInsepctionAIOutput'][17]['Remark'] = \
            data['output_data']['Missing_part_model']['missing_details']['Silencer']['remark']
        new['LeadInsepctionAIOutput'][17]['Processing_Time'] = data['output_data']['Missing_part_model'][
            'Processing Time']
        new['LeadInsepctionAIOutput'][17]['AIQCStatus'] = \
            data['output_data']['Missing_part_model']['missing_details']['Silencer']['Model_qc']
    else:
        new['LeadInsepctionAIOutput'][17]['AI_Model'] = 'Missing_part_model'
        new['LeadInsepctionAIOutput'][17]['AI_SubModel'] = 'Bumper (front and back)'
        new['LeadInsepctionAIOutput'][17]['PartName'] = ''
        new['LeadInsepctionAIOutput'][17]['model_status'] = \
            data['output_data']['Missing_part_model']['missing_details']['Bumper']['IsActive']
        new['LeadInsepctionAIOutput'][17]['model_result'] = \
            data['output_data']['Missing_part_model']['missing_details']['Bumper']['result']
        new['LeadInsepctionAIOutput'][17]['Remark'] = \
            data['output_data']['Missing_part_model']['missing_details']['Bumper']['remark']
        new['LeadInsepctionAIOutput'][17]['Processing_Time'] = data['output_data']['Missing_part_model'][
            'Processing Time']
        new['LeadInsepctionAIOutput'][17]['AIQCStatus'] = \
            data['output_data']['Missing_part_model']['missing_details']['Bumper']['Model_qc']

    # Wipers
    if data["output_data"]["vehicle_type_model"]["model_result"] == "Two wheeler":
        new['LeadInsepctionAIOutput'][18]['AI_Model'] = 'Missing_part_model'
        new['LeadInsepctionAIOutput'][18]['AI_SubModel'] = 'Seat'
        new['LeadInsepctionAIOutput'][18]['PartName'] = ''
        new['LeadInsepctionAIOutput'][18]['model_status'] = \
            data['output_data']['Missing_part_model']['missing_details']['Seat']['IsActive']
        new['LeadInsepctionAIOutput'][18]['model_result'] = \
            data['output_data']['Missing_part_model']['missing_details']['Seat']['result']
        new['LeadInsepctionAIOutput'][18]['Remark'] = \
            data['output_data']['Missing_part_model']['missing_details']['Seat']['remark']
        new['LeadInsepctionAIOutput'][18]['Processing_Time'] = data['output_data']['Missing_part_model'][
            'Processing Time']
        new['LeadInsepctionAIOutput'][18]['AIQCStatus'] = \
            data['output_data']['Missing_part_model']['missing_details']['Seat']['Model_qc']
    else:
        new['LeadInsepctionAIOutput'][18]['AI_Model'] = 'Missing_part_model'
        new['LeadInsepctionAIOutput'][18]['AI_SubModel'] = 'Wipers'
        new['LeadInsepctionAIOutput'][18]['PartName'] = ''
        new['LeadInsepctionAIOutput'][18]['model_status'] = \
            data['output_data']['Missing_part_model']['missing_details']['Wipers']['IsActive']
        new['LeadInsepctionAIOutput'][18]['model_result'] = \
            data['output_data']['Missing_part_model']['missing_details']['Wipers']['result']
        new['LeadInsepctionAIOutput'][18]['Remark'] = \
            data['output_data']['Missing_part_model']['missing_details']['Wipers']['remark']
        new['LeadInsepctionAIOutput'][18]['Processing_Time'] = data['output_data']['Missing_part_model'][
            'Processing Time']
        new['LeadInsepctionAIOutput'][18]['AIQCStatus'] = \
            data['output_data']['Missing_part_model']['missing_details']['Wipers']['Model_qc']

    # Headlights
    new['LeadInsepctionAIOutput'][19]['AI_Model'] = 'Missing_part_model'
    new['LeadInsepctionAIOutput'][19][
        'AI_SubModel'] = 'Headlights (front and back) - Head lamp/Tail lamp/Indicators/Fog Lamp (front and back)'
    new['LeadInsepctionAIOutput'][19]['PartName'] = ''
    new['LeadInsepctionAIOutput'][19]['model_status'] = \
        data['output_data']['Missing_part_model']['missing_details']['Headlights']['IsActive']
    new['LeadInsepctionAIOutput'][19]['model_result'] = \
        data['output_data']['Missing_part_model']['missing_details']['Headlights']['result']
    new['LeadInsepctionAIOutput'][19]['Remark'] = \
        data['output_data']['Missing_part_model']['missing_details']['Headlights']['remark']
    new['LeadInsepctionAIOutput'][19]['Processing_Time'] = data['output_data']['Missing_part_model']['Processing Time']
    new['LeadInsepctionAIOutput'][19]['AIQCStatus'] = \
        data['output_data']['Missing_part_model']['missing_details']['Headlights']['Model_qc']

    # Wheels
    if data["output_data"]["vehicle_type_model"]["model_result"] == "Two wheeler":
        new['LeadInsepctionAIOutput'][20]['AI_SubModel'] = 'Wheels (2)'
    else:
        new['LeadInsepctionAIOutput'][20]['AI_SubModel'] = 'Wheels (4)'
    new['LeadInsepctionAIOutput'][20]['AI_Model'] = 'Missing_part_model'
    new['LeadInsepctionAIOutput'][20]['PartName'] = ''
    new['LeadInsepctionAIOutput'][20]['model_status'] = \
        data['output_data']['Missing_part_model']['missing_details']['Wheels']['IsActive']
    new['LeadInsepctionAIOutput'][20]['model_result'] = \
        data['output_data']['Missing_part_model']['missing_details']['Wheels']['result']
    new['LeadInsepctionAIOutput'][20]['Remark'] = \
        data['output_data']['Missing_part_model']['missing_details']['Wheels']['remark']
    new['LeadInsepctionAIOutput'][20]['Processing_Time'] = data['output_data']['Missing_part_model']['Processing Time']
    new['LeadInsepctionAIOutput'][20]['AIQCStatus'] = \
        data['output_data']['Missing_part_model']['missing_details']['Wheels']['Model_qc']

    # Windshield
    new['LeadInsepctionAIOutput'][22]['AI_Model'] = 'Missing_part_model'
    new['LeadInsepctionAIOutput'][22]['AI_SubModel'] = 'Windshield (front and back) '
    new['LeadInsepctionAIOutput'][22]['PartName'] = ''
    # case-1, when both are true
    if data['output_data']['Windshield']['front']['Remark'] == "String" and data['output_data']['Windshield']['rear'][
        'Remark'] == "String":
        new['LeadInsepctionAIOutput'][22]['model_status'] = data['output_data']['Windshield']['front']['model_status']
        new['LeadInsepctionAIOutput'][22]['model_result'] = data['output_data']['Windshield']['front']['model_result']
        new['LeadInsepctionAIOutput'][22]['Remark'] = data['output_data']['Windshield']['front']['Remark']
    # case-2, when rear is False
    if data['output_data']['Windshield']['front']['Remark'] == "String" and data['output_data']['Windshield']['rear'][
        'Remark'] != "String":
        new['LeadInsepctionAIOutput'][22]['model_status'] = data['output_data']['Windshield']['rear']['model_status']
        new['LeadInsepctionAIOutput'][22]['model_result'] = data['output_data']['Windshield']['rear']['model_result']
        new['LeadInsepctionAIOutput'][22]['Remark'] = data['output_data']['Windshield']['rear']['Remark']
        # case-3, when front is False
    if data['output_data']['Windshield']['front']['Remark'] != "String" and data['output_data']['Windshield']['rear'][
        'Remark'] == "String":
        new['LeadInsepctionAIOutput'][22]['model_status'] = data['output_data']['Windshield']['front']['model_status']
        new['LeadInsepctionAIOutput'][22]['model_result'] = data['output_data']['Windshield']['front']['model_result']
        new['LeadInsepctionAIOutput'][22]['Remark'] = data['output_data']['Windshield']['front']['Remark']

    if data['output_data']['Windshield']['front']['Remark'] != "String" and data['output_data']['Windshield']['rear'][
        'Remark'] != "String":
        new['LeadInsepctionAIOutput'][22]['model_status'] = data['output_data']['Windshield']['front']['model_status']
        new['LeadInsepctionAIOutput'][22]['model_result'] = data['output_data']['Windshield']['front']['model_result']
        new['LeadInsepctionAIOutput'][22]['Remark'] = data['output_data']['Windshield']['front']['Remark']
    new['LeadInsepctionAIOutput'][22]['Processing_Time'] = data['output_data']['Windshield']['Processing Time']
    new['LeadInsepctionAIOutput'][22]['AIQCStatus'] = data['output_data']['Windshield']['Model_qc']

    # Dents and Damages Model
    # front panel
    new['LeadInsepctionAIOutput'][24]['AI_Model'] = 'Damage_Model'
    new['LeadInsepctionAIOutput'][24]['AI_SubModel'] = 'Front Panel'
    new['LeadInsepctionAIOutput'][24]['PartName'] = ''
    new['LeadInsepctionAIOutput'][24]['model_result'] = data['output_data']['DND']['model_result']
    new['LeadInsepctionAIOutput'][24]['Remark'] = data['output_data']['DND']['Remark']
    new['LeadInsepctionAIOutput'][24]['Processing_Time'] = data['output_data']['DND']['Processing Time']
    new['LeadInsepctionAIOutput'][24]['NoOfDamageCount'] = data['output_data']['DND']['panel_wise']['front']
    new['LeadInsepctionAIOutput'][24]['AIQCStatus'] = data['output_data']['DND']['Model_qc']
    new['LeadInsepctionAIOutput'][24]['model_status'] = data['output_data']['DND']["Is_Active"]
    # front right side panel
    if data["output_data"]["vehicle_type_model"]["model_result"] == "Car":
        new['LeadInsepctionAIOutput'][25]['AI_Model'] = 'Damage_Model'
        new['LeadInsepctionAIOutput'][25]['AI_SubModel'] = 'Front Right Side Panel'
        new['LeadInsepctionAIOutput'][25]['PartName'] = ''
        new['LeadInsepctionAIOutput'][25]['model_result'] = data['output_data']['DND']['model_result']
        new['LeadInsepctionAIOutput'][25]['Remark'] = data['output_data']['DND']['Remark']
        new['LeadInsepctionAIOutput'][25]['Processing_Time'] = data['output_data']['DND']['Processing Time']
        new['LeadInsepctionAIOutput'][25]['NoOfDamageCount'] = data['output_data']['DND']['panel_wise']['front_right']
        new['LeadInsepctionAIOutput'][25]['AIQCStatus'] = data['output_data']['DND']['Model_qc']
        new['LeadInsepctionAIOutput'][25]['model_status'] = data['output_data']['DND']["Is_Active"]
        # front left side panel
        new['LeadInsepctionAIOutput'][26]['AI_Model'] = 'Damage_Model'
        new['LeadInsepctionAIOutput'][26]['AI_SubModel'] = 'Front Left Side Panel'
        new['LeadInsepctionAIOutput'][26]['PartName'] = ''
        new['LeadInsepctionAIOutput'][26]['model_result'] = data['output_data']['DND']['model_result']
        new['LeadInsepctionAIOutput'][26]['Remark'] = data['output_data']['DND']['Remark']
        new['LeadInsepctionAIOutput'][26]['Processing_Time'] = data['output_data']['DND']['Processing Time']
        new['LeadInsepctionAIOutput'][26]['NoOfDamageCount'] = data['output_data']['DND']['panel_wise']['front_left']
        new['LeadInsepctionAIOutput'][26]['AIQCStatus'] = data['output_data']['DND']['Model_qc']
        new['LeadInsepctionAIOutput'][26]['model_status'] = data['output_data']['DND']["Is_Active"]
        # Rear_right, back right side panel
        new['LeadInsepctionAIOutput'][27]['AI_Model'] = 'Damage_Model'
        new['LeadInsepctionAIOutput'][27]['AI_SubModel'] = 'Back Right Side Panel'
        new['LeadInsepctionAIOutput'][27]['PartName'] = ''
        new['LeadInsepctionAIOutput'][27]['model_result'] = data['output_data']['DND']['model_result']
        new['LeadInsepctionAIOutput'][27]['Remark'] = data['output_data']['DND']['Remark']
        new['LeadInsepctionAIOutput'][27]['Processing_Time'] = data['output_data']['DND']['Processing Time']
        new['LeadInsepctionAIOutput'][27]['NoOfDamageCount'] = data['output_data']['DND']['panel_wise']['rear_right']
        new['LeadInsepctionAIOutput'][27]['AIQCStatus'] = data['output_data']['DND']['Model_qc']
        new['LeadInsepctionAIOutput'][27]['model_status'] = data['output_data']['DND']["Is_Active"]
        # rear_left, back left side panel
        new['LeadInsepctionAIOutput'][28]['AI_Model'] = 'Damage_Model'
        new['LeadInsepctionAIOutput'][28]['AI_SubModel'] = 'Back Left Side Panel'
        new['LeadInsepctionAIOutput'][28]['PartName'] = ''
        new['LeadInsepctionAIOutput'][28]['model_result'] = data['output_data']['DND']['model_result']
        new['LeadInsepctionAIOutput'][28]['Remark'] = data['output_data']['DND']['Remark']
        new['LeadInsepctionAIOutput'][28]['Processing_Time'] = data['output_data']['DND']['Processing Time']
        new['LeadInsepctionAIOutput'][28]['NoOfDamageCount'] = data['output_data']['DND']['panel_wise']['rear_left']
        new['LeadInsepctionAIOutput'][28]['AIQCStatus'] = data['output_data']['DND']['Model_qc']
        new['LeadInsepctionAIOutput'][28]['model_status'] = data['output_data']['DND']["Is_Active"]
    # rear, back side panel
    else:
        new['LeadInsepctionAIOutput'][25]['AI_Model'] = 'Damage_Model'
        new['LeadInsepctionAIOutput'][25]['AI_SubModel'] = 'Right Side Panel'
        new['LeadInsepctionAIOutput'][25]['PartName'] = ''
        new['LeadInsepctionAIOutput'][25]['model_result'] = data['output_data']['DND']['model_result']
        new['LeadInsepctionAIOutput'][25]['Remark'] = data['output_data']['DND']['Remark']
        new['LeadInsepctionAIOutput'][25]['Processing_Time'] = data['output_data']['DND']['Processing Time']
        new['LeadInsepctionAIOutput'][25]['NoOfDamageCount'] = data['output_data']['DND']['panel_wise']['right']
        new['LeadInsepctionAIOutput'][25]['AIQCStatus'] = data['output_data']['DND']['Model_qc']
        new['LeadInsepctionAIOutput'][25]['model_status'] = data['output_data']['DND']["Is_Active"]
        # front left side panel
        new['LeadInsepctionAIOutput'][26]['AI_Model'] = 'Damage_Model'
        new['LeadInsepctionAIOutput'][26]['AI_SubModel'] = 'Left Side Panel'
        new['LeadInsepctionAIOutput'][26]['PartName'] = ''
        new['LeadInsepctionAIOutput'][26]['model_result'] = data['output_data']['DND']['model_result']
        new['LeadInsepctionAIOutput'][26]['Remark'] = data['output_data']['DND']['Remark']
        new['LeadInsepctionAIOutput'][26]['Processing_Time'] = data['output_data']['DND']['Processing Time']
        new['LeadInsepctionAIOutput'][26]['NoOfDamageCount'] = data['output_data']['DND']['panel_wise']['left']
        new['LeadInsepctionAIOutput'][26]['AIQCStatus'] = data['output_data']['DND']['Model_qc']
        new['LeadInsepctionAIOutput'][26]['model_status'] = data['output_data']['DND']["Is_Active"]
    new['LeadInsepctionAIOutput'][29]['AI_Model'] = 'Damage_Model'
    new['LeadInsepctionAIOutput'][29]['AI_SubModel'] = 'Back Panel'
    new['LeadInsepctionAIOutput'][29]['PartName'] = ''
    new['LeadInsepctionAIOutput'][29]['model_result'] = data['output_data']['DND']['model_result']
    new['LeadInsepctionAIOutput'][29]['Remark'] = data['output_data']['DND']['Remark']
    new['LeadInsepctionAIOutput'][29]['Processing_Time'] = data['output_data']['DND']['Processing Time']
    new['LeadInsepctionAIOutput'][29]['NoOfDamageCount'] = data['output_data']['DND']['panel_wise']['rear']
    new['LeadInsepctionAIOutput'][29]['AIQCStatus'] = data['output_data']['DND']['Model_qc']
    new['LeadInsepctionAIOutput'][29]['model_status'] = data['output_data']['DND']["Is_Active"]
    # All Panels
    new['LeadInsepctionAIOutput'][30]['AI_Model'] = 'Damage_Model'
    new['LeadInsepctionAIOutput'][30]['AI_SubModel'] = 'All Panel'
    new['LeadInsepctionAIOutput'][30]['PartName'] = ''
    new['LeadInsepctionAIOutput'][30]['model_result'] = data['output_data']['DND']['model_result']
    new['LeadInsepctionAIOutput'][30]['Remark'] = data['output_data']['DND']['Remark']
    new['LeadInsepctionAIOutput'][30]['Processing_Time'] = data['output_data']['DND']['Processing Time']
    new['LeadInsepctionAIOutput'][30]['NoOfDamageCount'] = data['output_data']['DND']['Total_Damages']
    new['LeadInsepctionAIOutput'][30]['AIQCStatus'] = data['output_data']['DND']['Model_qc']
    new['LeadInsepctionAIOutput'][30]['model_status'] = data['output_data']['DND']["Is_Active"]
    ##########################################################################################################
    if data["output_data"]["vehicle_type_model"]["model_result"] == "Car":
        new['LeadInsepctionAIOutput'][31]['AI_Model'] = 'Video_Model'
        new['LeadInsepctionAIOutput'][31]['AI_SubModel'] = 'Identify  that Photos and Video is of same vehicle'
        new['LeadInsepctionAIOutput'][31]['PartName'] = ''
        if data["output_data"]["Number_Plate_Model"]["Video_AIQCStatus"] == "Approved":
            new['LeadInsepctionAIOutput'][31]['model_result'] = "Matched"
            new['LeadInsepctionAIOutput'][31]['model_status'] = data['output_data']['vehicle_type_model'][
                'vehicle_type_matches_with_input']
        else:
            new['LeadInsepctionAIOutput'][31]['model_result'] = "Not Matched"
            new['LeadInsepctionAIOutput'][31]['model_status'] = data['output_data']['vehicle_type_model'][
                'vehicle_type_matches_with_input']
        new['LeadInsepctionAIOutput'][31]['AIQCStatus'] = data["output_data"]["Number_Plate_Model"][
            "Video_AIQCStatus"]
        new['LeadInsepctionAIOutput'][31]['Video_Remarks'] = data["output_data"]["Number_Plate_Model"]["Video_Remarks"]
        new['LeadInsepctionAIOutput'][31]['Video_AIQCStatus'] = data["output_data"]["Number_Plate_Model"][
            "Video_AIQCStatus"]
        #################################################################################################################
        new['LeadInsepctionAIOutput'][33]['AI_Model'] = 'Video_Model'
        new['LeadInsepctionAIOutput'][33][
            'AI_SubModel'] = 'Proper 360 deg view, No Video frame change, no stop between, continous video shoot'
        new['LeadInsepctionAIOutput'][33]['PartName'] = ''
        if data["output_data"]["Image_caption"]["360_view"]:
            new['LeadInsepctionAIOutput'][33]['model_result'] = "Available"
            new['LeadInsepctionAIOutput'][33]['model_status'] = True
            new['LeadInsepctionAIOutput'][33]['Video_Remarks'] = "360 Degree  found in video"
            new['LeadInsepctionAIOutput'][33]['Video_AIQCStatus'] = "Approved"
            new['LeadInsepctionAIOutput'][33]['AIQCStatus'] = "Approved"
        else:
            new['LeadInsepctionAIOutput'][33]['model_result'] = "Not Available"
            new['LeadInsepctionAIOutput'][33]['model_status'] = False
            new['LeadInsepctionAIOutput'][33]['Video_Remarks'] = "360 Degree not found in video"
            new['LeadInsepctionAIOutput'][33]['Video_AIQCStatus'] = "Rejected"
            new['LeadInsepctionAIOutput'][33]['AIQCStatus'] = "Rejected"

    ########################################################################################################################
    # VehicleMismatch_Model
    new['LeadInsepctionAIOutput'][35]['AI_Model'] = 'VehicleMismatch_Model'
    new['LeadInsepctionAIOutput'][35]['AI_SubModel'] = 'Vehicle Type Mismatch'
    new['LeadInsepctionAIOutput'][35]['PartName'] = ''
    new['LeadInsepctionAIOutput'][35]['model_status'] = data['output_data']['vehicle_type_model']['model_status']
    new['LeadInsepctionAIOutput'][35]['model_result'] = data['output_data']['vehicle_type_model']['model_result']
    new['LeadInsepctionAIOutput'][35]['Match_Result'] = data['output_data']['vehicle_type_model'][
        'vehicle_type_matches_with_input']
    new['LeadInsepctionAIOutput'][35]['Remark'] = data['output_data']['vehicle_type_model']['Remark']
    new['LeadInsepctionAIOutput'][35]['Processing_Time'] = data['output_data']['vehicle_type_model']['Processing Time']
    new['LeadInsepctionAIOutput'][35]['AIQCStatus'] = data['output_data']['vehicle_type_model']['Model_qc']
    new['LeadInsepctionAIOutput'][35]['model_status'] = data['output_data']['vehicle_type_model']["model_status"]
    new['LeadInsepctionAIOutput'][35]['Video_Remarks'] = data["output_data"]["Number_Plate_Model"]["Video_Remarks"]
    new['LeadInsepctionAIOutput'][35]['Video_AIQCStatus'] = data["output_data"]["vehicle_type_model"][
        "Video_AIQCStatus"]
    new = final_check(new)
    save_path = f"{lead_id}/Processed/Vahan_qc.json"
    with open(save_path, "w") as write_file:
        json.dump(new, write_file)
    send_qc_response(lead_id)


def renaming_file(lead_id):
    path_re = f"{lead_id}/Processed/name_dict.pkl"
    infile = open(path_re, "rb")
    rename_dict = pickle.load(infile, encoding="bytes")
    infile.close()

    for key, val in rename_dict.items():
        angle = f"{lead_id}/AI/" + key
        if path.exists(angle):
            actual = f"{lead_id}/AI/" + val
            os.rename(angle, actual)


def temp_test_copy(lead_id, li):
    temp_img = []
    for i in li:
        temp_img.append(f"{lead_id}/Processed/{i}.jpg")
    final_folder = f"{lead_id}/Processed/DND/Dents"
    for i in temp_img:
        shutil.copy(i, final_folder)


def prepare_files(lead_id):
    path_to = f"{lead_id}/Processed/DND/Dents/*jpg"
    all_img = glob.glob(path_to)
    rpm = f"{lead_id}/Processed/rpm_crop.jpg"
    rpm_needle = f"{lead_id}/Processed/needle_rpm_crop.jpg"
    if path.exists(rpm_needle):
        all_img.append(rpm_needle)
    elif path.exists(rpm):
        all_img.append(rpm)

    rc_path = f"{lead_id}/Processed/RC/RC_predicted/*.jpg"
    all_rc_img = glob.glob(rc_path)
    for im in all_rc_img:
        all_img.append(im)
    # rc1=f"{lead_id}/Processed/rc1.jpg"
    # if path.exists(rc1):
    #     all_img.append(rc1)

    # rc2=f"{lead_id}/Processed/rc2.jpg"
    # if path.exists(rc2):
    #     all_img.append(rc2)

    resp = f"{lead_id}/Processed/Vahan_qc.json"
    if path.exists(resp):
        all_img.append(resp)
    final_folder = f"{lead_id}/AI"
    for i in all_img:
        shutil.copy(i, final_folder)
    try:
        renaming_file(lead_id)
    except Exception as e:
        pass


def merge_json_video(leadid):
    l = []
    final = f"{leadid}/AI_Video/final.json"
    missing = f"{leadid}/AI_Video/missing_part.json"
    plate = f"{leadid}/AI_Video/number_plate.json"
    ws_crop = f"{leadid}/AI_Video/ws_crop.json"

    with open(final, "w") as f:
        if path.exists(missing):
            with open(missing) as f1:
                data1 = json.load(f1)
                for i in range(len(data1)):
                    l.append(data1[i])
        if path.exists(plate):
            with open(plate) as f2:
                data2 = json.load(f2)
                for i in range(len(data2)):
                    l.append(data2[i])
        if path.exists(ws_crop):
            with open(ws_crop) as f3:
                data3 = json.load(f3)
                for i in range(len(data3)):
                    l.append(data3[i])
        json.dump(l, f)


def img_frames_video(leadid):
    merge_json_video(leadid)
    completename = leadid + "/AI_Video/"
    with open(leadid + '/AI_Video/final.json') as f:
        data = json.load(f)
    for fid in data:
        print(fid["filename"])
        openpath = completename + ntpath.basename(fid["filename"])
        img = cv2.imread(openpath)
        height, width = img.shape[:2]
        if ntpath.basename(fid["filename"]) == "front.jpg" or ntpath.basename(fid["filename"]) == "rear.jpg":
            label=""
            for obj in fid["objects"]:
                
                hconf = 0
                if (obj["name"] == "pvt" or obj["name"] == "taxi" or obj["name"] == "ws"):
                    if (obj["confidence"] > hconf):
                        hconf = obj["confidence"]
                        label = obj["name"]
                      #  print("labelllllllllllll",label)
                        x = int(round(obj["relative_coordinates"]["center_x"] * width))
                        y = int(round(obj["relative_coordinates"]["center_y"] * height))
                        w = int(round(obj["relative_coordinates"]["width"] * width))
                        h = int(round(obj["relative_coordinates"]["height"] * height))
                        xmin = int(x - (w / 2))
                        ymin = int(y - (h / 2))
                        xmax = int(x + (w / 2))
                        ymax = int(y + (h / 2))
                        if xmin < 0: xmin = 0
                        if ymin < 0: ymin = 0
                        if xmax < 0: xmax = 0
                        if ymax < 0: ymax = 0
                        t1 = (xmin, ymax)
                        b1 = (xmax, ymin)
                else:
                    hconf = obj["confidence"]
                    label = obj["name"]
                    x = int(round(obj["relative_coordinates"]["center_x"] * width))
                    y = int(round(obj["relative_coordinates"]["center_y"] * height))
                    w = int(round(obj["relative_coordinates"]["width"] * width))
                    h = int(round(obj["relative_coordinates"]["height"] * height))
                    xmin = int(x - (w / 2))
                    ymin = int(y - (h / 2))
                    xmax = int(x + (w / 2))
                    ymax = int(y + (h / 2))
                    if xmin < 0: xmin = 0
                    if ymin < 0: ymin = 0
                    if xmax < 0: xmax = 0
                    if ymax < 0: ymax = 0
                    t1 = (xmin, ymax)
                    b1 = (xmax, ymin)
                    img = cv2.rectangle(img, t1, b1, (0, 255, 0), 2)
                    img = cv2.putText(img, label, t1, cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2)
            if label == "pvt" or label == "taxi" or label == "ws":
                img = cv2.rectangle(img, t1, b1, (0, 255, 0), 2)
                img = cv2.putText(img, label, t1, cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
                cv2.imwrite(openpath, img)
        else:
            for obj in fid["objects"]:
                hconf = obj["confidence"]
                label = obj["name"]
                x = int(round(obj["relative_coordinates"]["center_x"] * width))
                y = int(round(obj["relative_coordinates"]["center_y"] * height))
                w = int(round(obj["relative_coordinates"]["width"] * width))
                h = int(round(obj["relative_coordinates"]["height"] * height))
                xmin_1 = int(x - (w / 2))
                ymin_1 = int(y - (h / 2))
                xmax_1 = int(x + (w / 2))
                ymax_1 = int(y + (h / 2))
                if xmin_1 < 0:
                    xmin_1 = 0
                if ymin_1 < 0:
                    ymin_1 = 0
                if xmax_1 < 0:
                    xmax_1 = 0
                if ymax_1 < 0:
                    ymax_1 = 0
                t1 = (xmin_1, ymax_1)
                b1 = (xmax_1, ymin_1)
                img = cv2.rectangle(img, t1, b1, (0, 255, 0), 2)
                img = cv2.putText(img, label, t1, cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2)
        cv2.imwrite(openpath, img)
