from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
import requests

# Create your views here.

def index(request):
    return render(request, "interactionChecker/index.html")

def interactions(request):
    if request.method == "GET" and len(request.GET["drug"]) >= 3:
        drug_list = request.GET["drug"].split(",")
        drug_list_length = len(drug_list)
        #when just one drug is typed do this
        if drug_list_length == 1:
            user_input = drug_list[0]
            getdrugs2 = requests.get(f"https://rxnav.nlm.nih.gov/REST/rxcui.json?name={user_input}&search=1")
            getdrugs2.raise_for_status

            drugRxcuiCodes = getdrugs2.json()
            drugCode_list = drugRxcuiCodes["idGroup"]["rxnormId"]
            drugs_to_unpack = []
            for code in drugCode_list:
                #this one gets me the drug information and which drugs it interacts with
                getdrugs = requests.get(f"https://rxnav.nlm.nih.gov/REST/interaction/interaction.json?rxcui={int(code)}")# use this instead because it get's all the data
                getdrugs.raise_for_status()
                drug_data = getdrugs.json()
                # I will give the drug_being_checked to the render function
                drug_being_checked = drug_data["interactionTypeGroup"][0]["interactionType"][0]["minConceptItem"]["name"]
                listOfInteractionPairs = drug_data["interactionTypeGroup"][0]["interactionType"][0]["interactionPair"]
                drugs_to_unpack.append(listOfInteractionPairs)
            return render(request, "interactionChecker/interactions.html", {
                "drugBeingChecked": drug_being_checked,
                "drugsToUnpack": drugs_to_unpack
            })

        elif drug_list_length > 1:
            drug_to_check_list = drug_list
            drugs_to_check_string = " vs ".join(drug_to_check_list)
            codes_for_interaction_list =[]
            for drug in drug_to_check_list:
                getdrugcode = requests.get(f"https://rxnav.nlm.nih.gov/REST/rxcui.json?name={drug}&search=1")
                getdrugcode.raise_for_status
                drugCode = getdrugcode.json()["idGroup"]["rxnormId"][0]
                codes_for_interaction_list.append(drugCode)
            print(codes_for_interaction_list)
            drugs_to_search = "+".join(codes_for_interaction_list)
            get_the_drug_interactions = requests.get(f"https://rxnav.nlm.nih.gov/REST/interaction/list.json?rxcuis={drugs_to_search}")
            get_the_drug_interactions.raise_for_status
            interaction_dictionary = get_the_drug_interactions.json()
            full_interaction_list = interaction_dictionary["fullInteractionTypeGroup"][0]["fullInteractionType"]
            return render(request, "interactionChecker/interactions.html", {
                "drugsToCheckString": drugs_to_check_string,
                "fullInteractionList": full_interaction_list
            })


    return  HttpResponseRedirect(reverse("index"))