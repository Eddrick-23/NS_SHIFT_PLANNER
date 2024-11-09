import streamlit as st
from database import database as database
import pandas as pd
from st_btn_group import st_btn_group
import zipfile
import io
import os


st.set_page_config(page_title="Shift Planner",page_icon=":military_helmet:",layout="wide")
st.title("Shift Planner")

if "has_rerun_on_upload" not in st.session_state:
      st.session_state.has_rerun_on_upload = None

#create sidebar that takes some inputs

#load the database names

if "namesd1MCC" not in st.session_state:
        st.session_state.namesd1MCC = set()
if "namesd2MCC" not in st.session_state:
        st.session_state.namesd2MCC = set()
if "namesd1HCC1" not in st.session_state:
        st.session_state.namesd1HCC1 = set()
if "namesd2HCC1" not in st.session_state:
        st.session_state.namesd2HCC1 = set()
if "namesd3" not in st.session_state:
        st.session_state.namesd3 = set()

if "💀DAY 1: MCC" not in st.session_state:
      st.session_state["💀DAY 1: MCC"]= database(location="MCC ",day=1)
if "😴DAY 1: HCC1" not in st.session_state:
      st.session_state["😴DAY 1: HCC1"] = database(location="HCC1",day=1)
if "💀DAY 2: MCC" not in st.session_state:
      st.session_state["💀DAY 2: MCC"]= database(location="MCC ",day=2)
if "😴DAY 2: HCC1" not in st.session_state:
      st.session_state["😴DAY 2: HCC1"]= database(location="HCC1",day=2)
if "NIGHT DUTY" not in st.session_state:
      st.session_state["NIGHT DUTY"] = database(location="MCC ",day=3)

if "D1Names" not in st.session_state:
      st.session_state.D1Names = set()
if "D2Names" not in st.session_state:
      st.session_state.D2Names = set()
if "D3Names" not in st.session_state:
      st.session_state.D3Names = set()


def add_name(name):
      n = name.strip().upper()
      day = st.session_state[st.session_state.db_to_update].day

      if n == "HCC1" or n == "MCC": #Invalid name as control centre location
            st.sidebar.error("Invalid name!")

      if n not in st.session_state[st.session_state.db_to_update].get_names() and n not in st.session_state[f"D{day}Names"]:
            st.session_state[st.session_state.db_to_update].add_name(n)
            st.session_state[f"D{day}Names"].add(n)
      else:
            st.sidebar.error("Name already exists!")
            
def remove_name(name_list):
      day = st.session_state[st.session_state.db_to_update].day

      for n in name_list:
         st.session_state[st.session_state.db_to_update].remove_name(n)
         st.session_state[f"D{day}Names"].remove(n)


#sidebar
st.session_state.db_to_update = st.sidebar.radio("Database",options=["💀DAY 1: MCC","😴DAY 1: HCC1","💀DAY 2: MCC","😴DAY 2: HCC1","NIGHT DUTY"],key="sidebaractivedb",horizontal=True)

sidebar_col11,sidebar_col12 = st.sidebar.columns(2)

name = sidebar_col11.text_input("Enter Name:")
if sidebar_col11.button("Submit"):
      add_name(name)
name_list = sidebar_col12.multiselect(label="Choose names to remove",options=st.session_state[st.session_state.db_to_update].get_names())
if sidebar_col12.button("Remove"):
      remove_name(name_list)


st.session_state.hided1_grid = st.sidebar.toggle("Hide DAY 1 grid")
st.session_state.hided2_grid = st.sidebar.toggle("Hide DAY 2 grid")
st.session_state.hided3_grid = st.sidebar.toggle("Hide DAY 3 grid")

#back to main page

col1, col2 = st.columns(2)

with col1:
      st.session_state.active_database = st.radio(label="Database",options=["💀DAY 1: MCC","😴DAY 1: HCC1","💀DAY 2: MCC","😴DAY 2: HCC1","NIGHT DUTY"],horizontal=True)
      st.session_state.active_name = st.selectbox(label="Name",options=st.session_state[st.session_state.active_database].get_names())
with col2:
      st.session_state.active_allocation_size = st_btn_group(mode="radio",buttons=[{"label":"First 30 min","value":"001"},{"label":"Full","value":"002"},{"label":"Last 30 min","value":"30"}],key="allocation_size",merge_buttons=True,size="compact",radio_default_index=1)
      st.session_state.active_location = st.radio(label="Location",options=["MCC ","HCC1"]) #whitespace after MCC for standard cell size
#button groups

def allocate_shift(hour): #call back function for buttons
      # set up appropriate timeblock to query
      main_time_block = hour + ":00:00" #actual time block e.g if left half @1200 > 1200/ right half > 1230
      other_time_block = hour+ ":30:00"  #other half if left half @1200, other half > 1230 etc.
      if st.session_state.active_allocation_size == "30":
            main_time_block,other_time_block = other_time_block,main_time_block #swap
      #check first if shift is allocated
      allocation_state1 = st.session_state[st.session_state.active_database].is_shift_allocated(time_block=main_time_block,name = st.session_state.active_name)
      allocation_state2 = None
      if st.session_state.active_allocation_size == "002":
            allocation_state2 = st.session_state[st.session_state.active_database].is_shift_allocated(other_time_block, name = st.session_state.active_name)
      #deal with allocation_state1
      if not allocation_state1: #if shift not allocated, allocate shift
            st.session_state[st.session_state.active_database].add_shift(location = st.session_state.active_location,time_block = main_time_block,name = st.session_state.active_name)
      else: 
            st.session_state[st.session_state.active_database].remove_shift(time_block = main_time_block,name = st.session_state.active_name)
      
      if allocation_state2 != None:
            if not allocation_state2: #allocate other half for FULL SHIFT OPTION
                  st.session_state[st.session_state.active_database].add_shift(location = st.session_state.active_location,time_block = other_time_block,name = st.session_state.active_name)
            else:
                  st.session_state[st.session_state.active_database].remove_shift(time_block = other_time_block,name = st.session_state.active_name)

def create_button_group():
    #set the time ranges first
    default_day_range = ["06","07","08","09","10","11","12","13","14","15","16","17","18","19","20"]
    if st.session_state.active_database == "NIGHT DUTY":
          default_day_range = ["21","22","23","00","01","02","03","04","05","06"]
    time_range = None
    if st.session_state.active_allocation_size in ["001","002"]:
         time_range = [item + "00" for item in default_day_range]
         
    elif st.session_state.active_allocation_size in ["30"]:
          time_range  = [item + "30" for item in default_day_range]

    if st.session_state.active_database in ["💀DAY 1: MCC","😴DAY 1: HCC1"]: #if day 1, remove 0600
              time_range.pop(0)
    
    #create the buttons:
    n_buttons = len(time_range)
    cols = st.columns(n_buttons)
    for n in range(n_buttons):
          with cols[n]:
                st.button(label=time_range[n],use_container_width=True,on_click=allocate_shift,kwargs={"hour":time_range[n][:2]})
if st.session_state.active_name != None:
      create_button_group()

#displaying dataframes
def format_keys(df1,df2):
        '''
            df1(pandas dataframe)
            df2(pandas dataframe)
            
            dataframes should have the same format. Merging the dataframes will just join the names.
            The "DAY" and "Time" Columns should be the same.

            This function reads two dataframes and returns formatted timeblocks that fit both dataframes. Such that they are always aligned.
        '''
        keys = []
        joined = []
        #iterate over df two rows at a time
        # we join the time slots only if 
        #1) no slots allocated at all in that 1h block
        #2) slots are allocated to the same person in that 1h block
        joined_df = df1.merge(df2)
        for i in range(0,len(joined_df),2):
            #get two rows at a time
            rows = joined_df.iloc[i:i+2]
            join_blocks = True
            for c in rows.columns[2:]:
                v1,v2 = rows[c].iloc[0],rows[c].iloc[1]

                if v1 != v2:
                    join_blocks = False
                    break
            keys.append(rows.Time.iloc[0][:-3]) #slice string for HH:MM format
            if join_blocks:
                joined.append(True)
            if not join_blocks:
                keys.append(rows.Time.iloc[1][:-3]) #slice string for HH:MM format
                joined.append(False)


        return keys, joined


if not st.session_state.hided1_grid:
      k,j = format_keys(st.session_state["💀DAY 1: MCC"].data,st.session_state["😴DAY 1: HCC1"].data)
      st.dataframe(st.session_state["💀DAY 1: MCC"].generate_formatted_df(keys = k, joined = j),hide_index=True,use_container_width=True)
      st.dataframe(st.session_state["😴DAY 1: HCC1"].generate_formatted_df(keys = k, joined = j),hide_index=True,use_container_width=True)

if not st.session_state.hided2_grid:
      k,j = format_keys(st.session_state["💀DAY 2: MCC"].data,st.session_state["😴DAY 2: HCC1"].data)
      st.dataframe(st.session_state["💀DAY 2: MCC"].generate_formatted_df(keys = k, joined = j),hide_index=True,use_container_width=True)
      st.dataframe(st.session_state["😴DAY 2: HCC1"].generate_formatted_df(keys = k, joined = j),hide_index=True,use_container_width=True)

bottom_col1,bottom_col2 = st.columns([0.3,0.7])

if not st.session_state.hided3_grid:
      bottom_col2.dataframe(st.session_state["NIGHT DUTY"].generate_formatted_df(),hide_index=True,use_container_width=True)

def display_hours():
      hours = {}
      d1MCC = st.session_state["💀DAY 1: MCC"].hours
      d1HCC1 = st.session_state["😴DAY 1: HCC1"].hours
      d2MCC = st.session_state["💀DAY 2: MCC"].hours
      d2HCC1 = st.session_state["😴DAY 2: HCC1"].hours
      nightduty = st.session_state["NIGHT DUTY"].hours

      for key,val in d1MCC.items():
            if key not in hours:
                  hours[key] = [0,0,0]
            hours[key][0] = val
      
      for key,val in d1HCC1.items():
            if key not in hours:
                  hours[key] = [0,0,0]
            hours[key][0] = val
      
      for key,val in d2MCC.items():
            if key not in hours:
                  hours[key] = [0,0,0]
            hours[key][1] = val
      for key,val in d2HCC1.items():
            if key not in hours:
                  hours[key] = [0,0,0]
            hours[key][1] = val
      for key,val in nightduty.items():
            if key not in hours:
                  hours[key] = [0,0,0]
            hours[key][2] = val
      
      for key,val in hours.items():
            val.append(sum(val))
      
      df = pd.DataFrame(data=hours,index=["DAY 1","DAY 2","DAY 3","TOTAL"]).T
      df.loc["total"] = df.sum()
      
      
      return df

hour_count = display_hours()
      
bottom_col1.dataframe(hour_count)

#uploading and downloading files

# Function to extract and read CSV files from the zip archive
def extract_and_read_csv(zip_file):
    # Create a temporary directory to extract files to
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall("extracted_files")

    # List the CSV files in the extracted folder
    csv_files = [f for f in os.listdir("extracted_files") if f.endswith('.csv')]

    # Create a dictionary to store DataFrames
    dfs = {}

    # Read each CSV file into a pandas DataFrame
    for csv_file in csv_files:
        file_path = os.path.join("extracted_files", csv_file)
        df = pd.read_csv(file_path)
        dfs[csv_file] = df

    # Clean up: Remove the extracted files after reading
    for csv_file in csv_files:
        os.remove(os.path.join("extracted_files", csv_file))

    return dfs


st.session_state.zip_file = st.sidebar.file_uploader(label="Upload zip of saved work",type="zip")

if st.session_state.zip_file is not None and not st.session_state.has_rerun_on_upload:
    # Convert uploaded file to BytesIO object
    zip_file_bytes = io.BytesIO(st.session_state.zip_file.read())
    
    # Extract and read CSV files into DataFrames
    dataframes = extract_and_read_csv(zip_file_bytes)
    
    # Display the DataFrames
    st.session_state["💀DAY 1: MCC"].set_data(dataframes["DAY1MCC.csv"].drop('Unnamed: 0', axis=1))
    st.session_state.namesd1MCC = st.session_state["💀DAY 1: MCC"].names
    st.session_state["💀DAY 2: MCC"].set_data(dataframes["DAY2MCC.csv"].drop('Unnamed: 0', axis=1))
    st.session_state.namesd2MCC = st.session_state["💀DAY 2: MCC"].names
    st.session_state["😴DAY 1: HCC1"].set_data(dataframes["DAY1HCC1.csv"].drop('Unnamed: 0', axis=1))
    st.session_state.namesd1HCC1 = st.session_state["😴DAY 1: HCC1"].names
    st.session_state["😴DAY 2: HCC1"].set_data(dataframes["DAY2HCC1.csv"].drop('Unnamed: 0', axis=1))
    st.session_state.namesd2HCC1 = st.session_state["😴DAY 2: HCC1"].names
    st.session_state["NIGHT DUTY"].set_data(dataframes["NIGHTDUTY.csv"].drop('Unnamed: 0', axis=1))
    st.session_state.namesd3 = st.session_state["NIGHT DUTY"].names
    st.session_state.D1Names = st.session_state.namesd1MCC.union(st.session_state.namesd1HCC1)
    st.session_state.D2Names = st.session_state.namesd2MCC.union(st.session_state.namesd2HCC1)
    st.session_state.D3Names = st.session_state.namesd3.copy()
    st.session_state.has_rerun_on_upload = True
    st.rerun()



def create_zip():
      #takes all dataframes from each database, convert to csv, store as zip file

      buf = io.BytesIO()
      with zipfile.ZipFile(buf, "x") as myzip: # set the mode parameter to x to create and write a new file
            myzip.writestr("DAY1MCC.csv", st.session_state["💀DAY 1: MCC"].data.to_csv()) # convert df to .csv and name it
            myzip.writestr("DAY1HCC1.csv", st.session_state["😴DAY 1: HCC1"].data.to_csv()) 
            myzip.writestr("DAY2MCC.csv", st.session_state["💀DAY 2: MCC"].data.to_csv()) 
            myzip.writestr("DAY2HCC1.csv", st.session_state["😴DAY 2: HCC1"].data.to_csv())
            myzip.writestr("NIGHTDUTY.csv",st.session_state["NIGHT DUTY"].data.to_csv())

      return buf


st.sidebar.download_button(label="Download zip",data=create_zip().getvalue(),file_name="Planning.zip",mime="data/zip",use_container_width=True)

day1warnings,day2warnings,day3warnings = st.columns(3)

def validate_shifts(df1,df2,day):
      '''
      Method checks that approriate strength is allocated to control centres for mounting hours
      Best to call when hours are all allocated as computation is resource heavy
      '''
      result = []
      if day == 1 or day == 2:
            joined_df = df1.merge(df2)

            for idx,row in joined_df.iterrows():
                  freq_data = row[2:].value_counts() #get count of MCC and HCC1
                  
                  if  "HCC1" not in row.values and "MCC " not in row.values:
                        result.append(f"WARNING(INSUFFICIENT STRENGTH):At {row.Time}. No one in both control centres.")
                  elif "HCC1" not in row.values: # Check if no one in HCC1
                        result.append(f"WARNING(MISALLOCATION): At {row.Time}. MCC:{freq_data.MCC}. No one in HCC1.")
                  elif "MCC " not in row.values: # Check if no one in MCC
                        result.append(f"WARNING(MISALLOCATION): At {row.Time}. HCC1:{freq_data.HCC1}. No one in MCC.")
                  elif freq_data["MCC "] + freq_data.HCC1 < 4: # Check if insufficient strength
                        result.append(f"WARNING(INSUFFICIENT STRENGTH): At {row.Time}. MCC:{freq_data['MCC ']}, HCC1:{freq_data.HCC1}")
                  elif freq_data.HCC1 != 2 or freq_data["MCC "] != 2: # Check if either MCC or HCC1 not exactly 2
                        result.append(f"WARNING(MISALLOCATION): At {row.Time}. MCC:{freq_data['MCC ']}, HCC1:{freq_data.HCC1}")
      elif day == 3:
            for idx,row in df1.iterrows():
                  freq_data = row[2:].value_counts() #get count of MCC
                  if not hasattr(freq_data,"MCC "):
                        result.append(f"WARNING(INSUFFICIENT STRENGTH, NEED 2): AT Day {row.Time}. MCC:0")
                  elif row.Time not in ["06:00:00","06:30:00"] and freq_data['MCC ']< 2:
                        result.append(f"WARNING(INSUFFICIENT STRENGTH, NEED 2): AT Day {row.DAY},{row.Time}. MCC:{freq_data['MCC ']})")
                  elif row.Time in ["06:00:00","06:30:00"] and freq_data['MCC '] < 3:
                        result.append(f"WARNING(INSUFFICIENT STRENGTH, NEED AT LEAST 3): AT Day {row.Time}. MCC:{freq_data['MCC ']})")
      
      return result

day1warnings.text("DAY 1")
day2warnings.text("DAY 2")
day3warnings.text("DAY 3")

if hour_count["DAY 1"].iloc[-1] >= 56:
      warnings = validate_shifts(st.session_state["💀DAY 1: MCC"].data,st.session_state["😴DAY 1: HCC1"].data,day=1)
      if warnings == []:
            day1warnings.write("Shifts validated. No warnings")

      else:
            for w in warnings:
                  day1warnings.write(w)
if hour_count["DAY 2"].iloc[-1] >= 60:
      warnings = validate_shifts(st.session_state["💀DAY 2: MCC"].data,st.session_state["😴DAY 2: HCC1"].data,day=2)

      if warnings == []:
            day2warnings.write("Shifts validated. No warnings")
      
      else:
            for w in warnings:
                  day2warnings.write(w)

if hour_count["DAY 3"].iloc[-1] >=21:
      warnings = validate_shifts(df1=st.session_state["NIGHT DUTY"].data,df2=None,day=3)

      if warnings == []:
            day3warnings.write("Shifts validated. No warnings")
      
      else:
            for w in warnings:
                  day3warnings.write(w)