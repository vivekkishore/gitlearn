import os
from dotenv import load_dotenv
#Load_dotenv() # It must be before llama_index import
from llama_index.core import GPTVectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage,VectorStoreIndex
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.core import Settings
from llama_index.core import ServiceContext, set_global_service_context
import nest_asyncio
import traceback
import json
import traceback
nest_asyncio.apply()


api_key = "81eb970a1f314fcb8fae048c87374ed1"
azure_endpoint = "https://factexpdaiopi02.openai.azure.com/"
api_version = "2024-02-15-preview"

llm = AzureOpenAI(
    model="gpt-4-32k",
    deployment_name="gpt-4-32k",
    api_key=api_key,
    azure_endpoint=azure_endpoint,
    api_version=api_version,
)
#Use_Case_Scenario = []
Final_Outcome = []
Main_Use_Case = []
Main_Use_Case_items = []
count = 0
# You need to deploy your own embedding model as well as your own chat completion model
embed_model = AzureOpenAIEmbedding(
    model="text-embedding-ada-002",
    deployment_name="text-embedding-ada-002",
    api_key=api_key,
    azure_endpoint=azure_endpoint,
    api_version=api_version,
)
Settings.llm = llm
Settings.embed_model = embed_model

documents = SimpleDirectoryReader('./data').load_data()

service_context = ServiceContext.from_defaults(
  llm=llm,
  embed_model=embed_model
)


custom_llm_index = VectorStoreIndex.from_documents(
    documents, service_context=service_context
)


def Generate_Test_Scenario(Functional_FLow_Name,Sub_Flow_Name):
    from llama_index.core import Prompt
    import nest_asyncio
    nest_asyncio.apply()

    
    # Define a custom prompt
    template_use_case = (
        "You are an inteligent and expert in finding out the use case name, try to find its related use case name from Alternate Flow and Exception Flow, provided the context information. \n"
        "---------------------\n"
        "{context_str}"
        "\n---------------------\n"
        """You are an inteligent and expert in finding out the use case name equally from multiple interlinked 
    documents about a tool. create a full list of use case names with use case id, provided Use case name with Function name in comma (,) seprated{query_str}.Format ech Use case with '###' sepration. cover all aspects including functionality, performance, security, and user interface.

    The answer should be dictionary in json format and dont put any quotations or string outside the json:
    1. **Use Case Name:** A brief name of test Topic.
    2. **Use Case ID:** Its Use case ID
    **End of Topic**
    Please adhere to the above template for each Use case.Formated in a readable manner and each test scenarios content has to be strictly seprated by ####."""
    )
    qa_template_use_case = Prompt(template_use_case)
    #Functional_FLow_Name = "Fare Payment"
    #Sub_Flow_Name = "Farecard"
    Function_Sub_Flow_name = Functional_FLow_Name +" , "+Sub_Flow_Name
    query_engine = custom_llm_index.as_query_engine(text_qa_template=qa_template_use_case)
    print(Function_Sub_Flow_name)
    response = query_engine.query(Function_Sub_Flow_name)
    Use_Case_Name = response.response
    Use_Case_Name = json.loads(Use_Case_Name)
    print(Use_Case_Name)
    return Use_Case_Name

from llama_index.core import Prompt
def Generate_TestScenario(Name_of_use_case):
    # Define a custom prompt
    template = (
        "We have provided context information, always try to go through Use case description, pre conditions and step with descriptions . \n"
        "---------------------\n"
        "{context_str}"
        "\n---------------------\n"
        """You are a seasoned QA engineer tasked with consolidating test scenarios equally from multiple interlinked 
    documents about a tool. create a comprehensive list of test scenarios for each Use case provided {query_str} and for exception flow and alternate flow please dont be general, be specific to use case , ensuring balanced coverage across all documents. cover all aspects including functionality, performance, security, and user interface.
    Note: Dont mention UI related test scenario or UI related functionality and Please consider device name's like BFTP ,TTC and Transit Agency names
    Each test scenarios should contain the follwoing information and the answer should be dictionary in json format and its key should be Test Scenario no:
    1. **Test scenarios:** A descriptive title of test scenario.
    2. **Description:** A detail descrition of the test scenario.
    3. **Expected Result:** Expected Result of the test scenario.
    **End of Topic**
    Please adhere to the above template for each test scenarios. Generate test scenarios."""
    )
    qa_template = Prompt(template)
    query_engine = custom_llm_index.as_query_engine(text_qa_template=qa_template)
    response = query_engine.query(Name_of_use_case)
    print("*****************************************")
    print(response.response)
    Test_Scenario = response.response
    print("------------------------------------------")
    Test_Scenario = json.loads(Test_Scenario)
    return Test_Scenario
    
def run_all(Functional_FLow_Name,Sub_Flow_Name):
    Generate_Data = Generate_Test_Scenario(Functional_FLow_Name,Sub_Flow_Name)
    print("Use Case Generated and going for test sceario")
    Use_Case_Scenario = []
    try:        
        
        for itm, val in Generate_Data.items():  
            try:     
                print("Inside the Generated_Data loop") 
                if isinstance(val, list):
                    for items in val:    
                        print("Inside the Items Generated Data Loop")                
                        if isinstance(items, dict):
                            
                            Output = {  "Function_Flow_Name":"",
                                        "Sub_Flow_Name":"",
                                        "Use_Case_Name":"",
                                        "Test_Scnario":"",
                                        "Test_Sce_Description":""}
                            Output["Function_Flow_Name"] = str(Functional_FLow_Name)
                            Output["Sub_Flow_Name"] = str(Sub_Flow_Name)
                            Output["Use_Case_Name"] = str(items["Use Case Name"])
                            Main_Use_Case.append(str(items["Use Case Name"]))
                            Use_Case_Scenario.append(Output)
            except:
                traceback.print_exc()
    except:
        traceback.print_exc()
        #print("There is issue in the data")
    print("Use Case Scenario List")
    print(Use_Case_Scenario)
    print(Main_Use_Case)
    try:
        for items in Use_Case_Scenario:
            print("items in Use case below")
            print(items)
            use_case = str(items["Use_Case_Name"])
            if use_case in Main_Use_Case and use_case in Main_Use_Case_items: 
                print("Use Case already persent in Main Use case file")                     
            else:
                Main_Use_Case_items.append(use_case)
                Generated_Output =  Generate_TestScenario(items["Use_Case_Name"])
                #Generated_Output = json.loads(Generated_Output)
                print("Generated Test Scenarios")
                print(Generated_Output)
                try:
                    for ind,scenario in Generated_Output.items():
                        print("for scenarios part")
                        print(scenario)
                        output ={"Function_Flow_Name":"",
                                "Sub_Flow_Name":"",
                                "Use_Case_Name":"",
                                "Test_Scnario":"",
                                "Test_Sce_Description":"",
                                "Expected_Results":""}
                        output["Function_Flow_Name"] = str(Functional_FLow_Name)
                        output["Sub_Flow_Name"] = str(Sub_Flow_Name)
                        output["Use_Case_Name"] = use_case
                        output["Test_Scnario"] = scenario["Test scenarios"]
                        output["Test_Sce_Description"] = scenario["Description"]
                        output["Expected_Results"] = scenario["Expected Result"]
                        Final_Outcome.append(output)
                    #print("Use Case Number :" + str(count))
                    print("Use Case Name :"+str(items["Use_Case_Name"]))    
                except:
                    traceback.print_exc()        
    except:
        traceback.print_exc()
    with open("list_data1.txt", "w") as file:
        json.dump(Main_Use_Case_items, file)
    with open('Scenario_Data_New_data_v3.json', 'w') as f:  #changed file name
        json.dump(Final_Outcome, f)
    return "Data Generated Succefully"


if __name__ == '__main__':
    Data = {
    "Use Case 1": {
    "Test Topic": "Fare Payment",
    "Test ID": "R6",
    "Functionalities": ["Farecard", "Tickets", "e-Tickets", "Virtual Card", "Open Payments", "With/Without audio messages"]
    },
    "Use Case 2": {
    "Test Topic": "Query a Farecard",
    "Test ID": "R2",
    "Functionalities": ["Tickets", "Virtual Card", "With/Without audio messages"]
    },
    "Use Case 3": {
    "Test Topic": "Cardholder profile changes",
    "Test ID": "R1",
    "Functionalities": ["Change universal concession", "Change SP specific concession", "Change card language profile", "Default Trip", "Block/Unblock"]
    },
    "Use Case 4": {
    "Test Topic": "Inspection",
    "Test ID": "R6",
    "Functionalities": ["Farecard", "Tickets", "e-Tickets", "With/Without audio messages", "Accept inspection", "Written warning", "Verbal warning", "Pay Fare", "Provincial offense notice (PON)"]
    },
    "Use Case 5": {
    "Test Topic": "Farecard Sales",
    "Test ID": "R2",
    "Functionalities": ["Farecard Sale", "E-Purse load", "Period pass load", "Paper Tickets", "Tickets", "Special Tickets", "Upgrades", "Other Products", "Vouchers", "Service Guarantee"]
    },
    "Use Case 6": {
    "Test Topic": "Reversals",
    "Test ID": "R1",
    "Functionalities": ["e-Purse payment reversal", "Period pass load reversal"]
    },
    "Use Case 7": {
    "Test Topic": "Refunds",
    "Test ID": "R6",
    "Functionalities": ["E-Purse balance refund", "Period pass refund", "Ticket/Special Ticket refund", "Other products"]
    },
    "Use Case 8": {
    "Test Topic": "Counters",
    "Test ID": "R2",
    "Functionalities": ["Activate", "Increment", "Configure haptic feedback", "Check counter summary"]
    },
    "Use Case 9": {
    "Test Topic": "GPS",
    "Test ID": "R1",
    "Functionalities": ["Enable/Disable GPS", "Select new route and line", "Override inspection location"]
    },
    "Use Case 10": {
    "Test Topic": "Training Mode",
    "Test ID": "R6",
    "Functionalities": ["Power on", "Shut down", "Reboot"]
    },
    "Use Case 11": {
    "Test Topic": "Passcode",
    "Test ID": "R2",
    "Functionalities": ["Enter lock screen passcode", "Change passcode", "Reset passcode", "Mandatory periodic passcode reset"]
    },
    "Use Case 12": {
    "Test Topic": "Operator sign-in",
    "Test ID": "R1",
    "Functionalities": ["First-time user", "Existing user", "Operator sign-off"]
    },
    "Use Case 13": {
    "Test Topic": "Modify screen brightness",
    "Test ID": "R6",
    "Functionalities": ["Modify audio tone volume"]
    },
    "Use Case 14": {
    "Test Topic": "Battery",
    "Test ID": "R2",
    "Functionalities": ["Operator checks battery power level", "SA Tool battery drops below the low battery threshold", "SA Tool battery dies"]
    },
    "Use Case 15": {
    "Test Topic": "Check SA Tool device information",
    "Test ID": "R1",
    "Functionalities": ["Switch device mode between different SPs (DISTANCE BASED TRANSIT and Distance based Transit only)"]
    },
    "Use Case 16": {
    "Test Topic": "Device states",
    "Test ID": "R6",
    "Functionalities": ["Operator switches SA Tool from standby to in-service state", "Operator switches SA Tool from in-service to standby state", "SA Tool switches to standby state after a configurable time of inactivity", "Operator switches to a third-party application"]
    },
    "Use Case 17": {
    "Test Topic": "Check Shift statistics",
    "Test ID": "R2",
    "Functionalities": ["Print shift statistics", "View historical reports"]
    },
    "Use Case 18": {
    "Test Topic": "Establish Wi-Fi or cellular network connection",
    "Test ID": "R1",
    "Functionalities": ["Establish Printer Connection", "Establish Payment Terminal Connection"]
    },
    "Use Case 19": {
    "Test Topic": "Change operator language",
    "Test ID": "R6",
    "Functionalities": ["In-App Training and FAQ", "Download Remote Lists"]
    }
    }

    try:
        for fnc , sub_fun in Data.items():
            print("Started Generating test Case funtion flow name")
            print(sub_fun["Test Topic"])
            if isinstance(sub_fun["Functionalities"], list):
                print("------------------------------------")
                for new_items in sub_fun["Functionalities"]:
                    print(("Started Generating test Case for sub funtion flow name"))
                    print(new_items)
                    run_all(str(sub_fun["Test Topic"]),str(new_items))
                    
                print("*************************************")
    except:
        traceback.print_exc()

    
