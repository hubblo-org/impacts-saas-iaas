#!/usr/bin/python3
import os.path
import csv

from posixpath import exists
from pprint import pprint

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

impact_criterias = {
    "adpe": "Epuisement des ressources abiotiques naturelles - éléments - kg Sb eq.",
    "adpf": "Epuisement des ressources abiotiques naturelles - fossiles - MJ",
    "ap": "Acidification - mol H+ eq.",
    "ctue": "Ecotoxicité - CTUe",
    "gwp": "Changement  climatique - kg CO2 eq.",
    "ir": "Radiations ionisantes - kBq U235 eq.",
    "pm": "Emissions de particules fines - Disease occurrence",
    "pocp": "Création d'ozone photochimi que - kg NMVOC eq.",
    "mips": "MIPS - kg",
    "wp": "Production de déchets - kg",
    "pe": "Consommation d'énergie primaire - MJ",
    "fe": "Consommation d'énergie finale (usage) - MJ"
}

tiers = {
    "devices": "Tier 1 (devices)",
    "network": "Tier 2 (network)",
    "datacenter": "Tier 3 (datacenter)",
    "total": "Total"
}
tiers_table = [ "devices", "network", "datacenter", "total" ]

def get_impact_criteria_short(header):
    for k, v in impact_criterias.items():
        if (v.strip().replace('\n', ' ') == header.strip().replace('\n', ' ')) or \
            (v.strip().replace('\n', '') == header.strip().replace('\n', ' ')):
            return k
    return None

def get_gdocs_data(tab):
    parameters = {
        "Service Type": "B3",
        "Size (GB)": "B4",
        "Service use duration": "B5",
        "DC Location": "B9"
    }

    results_range = "{}!B27:M31".format(tab)

    # If modifying these scopes, delete the file token.json.
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

    # The ID and range of a sample spreadsheet.
    SAMPLE_SPREADSHEET_ID = "1NkqzASrqKoMLy6bRBcukZvrmjVZ8JGkLlTL3LoMU17A"

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
      creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
          creds.refresh(Request())
        else:
          flow = InstalledAppFlow.from_client_secrets_file(
              "credentials.json", SCOPES
          )
          creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
          token.write(creds.to_json())

    try:
        service = build("sheets", "v4", credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()

        results = (
            sheet.values()
            .get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=results_range)
            .execute()
        )

        params = {}
        for k,v in parameters.items():
            params[k] = (
                sheet.values()
                .get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="{}!{}".format(tab, v))
                .execute()
            )

        pprint(params)

        # results['values'][0] -> header
        # results[values'][1:] -> values
        headers = ["dc_location", "service_type", "service_use_duration", "size_gb", "tier"]
        for h in results['values'][0]:
            header = h.strip().replace('\n', ' ')
            k = get_impact_criteria_short(header)
            print("k: {}".format(k))
            if k is not None:
                headers.append(k.strip().replace(' ', '').replace('\n', ''))

        data = []

        j = 0
        for v in results['values'][1:]:
            i = 0
            row = {
                "dc_location": params["DC Location"]["values"][0][0],
                "service_type": "{}".format(params["Service Type"]["values"][0][0]),
                "service_use_duration": params["Service use duration"]["values"][0][0],
                "size_gb": params["Size (GB)"]["values"][0][0],
                "tier": tiers_table[j]
            }
            for h in results['values'][0]:
                k = get_impact_criteria_short(h)
                if k is None:
                    print("k: {} h: {}".format(k, h))
                row[k] = float(v[i].replace('E', 'e').replace(',', '.'))
                i = i + 1
            data.append(row)
            j = j + 1

        return headers, data

    except HttpError as err:
        print(err)

    return None, None

def main():

    headers, data = get_gdocs_data("Storage Evaluation")

    pprint(headers)

    pprint(data)
    storage_file = "storage_impact.csv"
    if not exists(storage_file):
        with open(storage_file, "w") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data)
    with open(storage_file, "a+") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writerows(data)

if __name__ == '__main__':
    main()

#for src_file in ["storage_1.csv", "storage_2.csv"]:
#    if exists(src_file):
#        with open(src_file, "r") as fs_sto:
#            for l in fs_sto.readlines():
#                if l.startswith("Service Type"):
#
#                if "GWP" in l:
#                    cols = l.split(",")
#                    impact_criterias = cols[1:]
#                else:
#                    if l.startswith("Tier") or l.startswith("Total"):
#                        cols = l.split(",")
#                        tier = cols[0]
#                        values = cols[1:]
#
#                        # use_case,tier_1,tier_2,tier_3,total
#                        # storage
