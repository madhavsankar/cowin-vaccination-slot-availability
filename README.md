# CoWIN vaccination slot availability using Python

Script to check the available slots for Covid-19 Vaccination Centers from CoWIN API in India with the added feature to sort by the distance between your location and the vaccination center.

<!---
[Link to the Website](https://cowin-vaccination-appointment.herokuapp.com/)
-->

The Indian Government has blocked the API for crawlers, but we are good to go!

[Link to the article](https://analyticsindiamag.com/data-scientist-creates-python-script-to-track-available-slots-for-covid-vaccinations/)
&nbsp;
# Usage
- Clone the repository.
- The tool only works with Indian IP addresses so disconnect your VPN if needed.
- Enter the command - `cd cowin-vaccination-slot-availability-main/`
- Install all the dependencies - `pip3 install -r requirements.txt`
- Run the python application - `streamlit run app.py`
&nbsp;

# Demo
![](https://github.com/bhattbhavesh91/cowin-vaccination-slot-availability/blob/main/demo/demo_1.gif)

# Optimization
- Specially optimized for Chennai locations. All the pincode coordinates are pre-loaded. To repro this for other locations, create a function similar to 'write_chennai_coordinates' with the concerned pincode list as a csv.
Note: The solution still works for other locations and does return accurate distances. Optimization is to fasten the process and reduce the page load latency.
