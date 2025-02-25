import dash
from dash import html, dcc, callback, Input, Output, State, Dash, page_container
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import jobData
import ast



class MainApplication:
    def __init__(self):
        self.__app = Dash(
            __name__,
            use_pages=True,
        )
        self.set_layout()


    @property
    def app(self):
        return self.__app




tech = jobData.getTechs()
popTechs = jobData.getPopTechs()

dataCounted = pd.read_csv("app/AI_output_counted.csv")
counted_calcs = [[ast.literal_eval(x.lower()), y] for x, y in zip(dataCounted['Techs'], dataCounted['Count'])]

listing_count = 2807

color_map_pie = [
   "#124559",
   "#279AF1",
   "#7CDDF4",
   "#C2FFF9",
    "#BEAEC1",
    "#D7263D"
    ]  
#fig = px.line(df)

app = dash.Dash(__name__,external_stylesheets=[dbc.themes.SLATE])

#matchData = pd.read_csv("match.csv")
matchData = pd.DataFrame(data={"Match Percentage":[100,90,80,70,60,50,40,30,20,10,0], "Market Percentage":[0,0,0,0,0,0,0,0,0,0,100]})
pieData = matchData

matchFig = px.bar(matchData, x="Match Percentage", y="Market Percentage",  color="Match Percentage", color_continuous_scale="Bluered_r")
matchFig.update_xaxes(autorange="reversed", tickmode="array", tickvals = [100,90,80,70,60,50,40,30,20,10,0], ticktext=["Full Match", "90%", "80%", "70%", "60%", "50%", "40%","30%", "20%","10%","Not Qualified" ])
matchFig.update_yaxes( tickmode="array", tickvals = [100,90,80,70,60,50,40,30,20,10,0], ticktext=["100% of jobs", "90%", "80%", "70%", "60%", "50%", "40%","30%", "20%","10%","No Matches" ])
matchFig.update_layout(title_text="Tech Stack vs Market")

pieFig = px.pie(pieData, values="Match Percentage", names="Market Percentage",  hole=.2, color_discrete_sequence=color_map_pie)
#pieFig.update_xaxes(autorange="reversed", tickmode="array", tickvals = [100,75,50,25,0], ticktext=["Full Match", "75%+", "50%+", "25+%","Not Qualified" ])
#pieFig.update_yaxes( tickmode="array", tickvals = [100,75,50,25,0], ticktext=["100% of jobs", "75%+", "50%+", "25+%","No Matches" ])

upgradeFigure = px.bar()

upgradeFigure.update_layout(
    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    title="Tech Stack vs Market"
)

#print("wtf")

app.layout = [
   html.H1(title="??", children="Known Techstack:"),
   html.Div(id="dropdownDiv", children= [dcc.Dropdown(tech, id='known-dropdown',multi=True)]),
   html.Div(id="pieDiv", children = [dcc.Graph(id="pie-graph", figure=pieFig)] ),
   html.Div(id="matchDiv", children=
            [dcc.Graph(id='match-graph',figure=matchFig)]),
   
  html.Div(id = "upgradeDiv" , children=[
     html.Button("Show me what goes well with my tech stack", id="learn_button",
                  n_clicks=0 ), 
                  dcc.Graph(id="learn-graph", figure=upgradeFigure)]),
  html.Div(id="popularityText", children=[
                 html.Div(className="factDiv", 
                        children=dcc.Markdown(''' ## Top 10 
      1. Python  
      2. Java  
      3. Javascript  
      4. AWS  
      5. SQL  
      6. GIT  
      7. C#  
      8. React  
      9. Docker  
      10.Azure  ''')),
             html.Div(className="factDiv", 
                        children=dcc.Markdown('''# 9.35  
Average technologies''')),
            html.Div(className="factDiv", 
                        children=dcc.Markdown('''# 8  
Median technologies''')),
            html.Div(className="factDiv", 
                        children=dcc.Markdown('''# 79
max in one listing (__yikes__) ''')),
            html.Div(className="factDiv", 
                        children=dcc.Markdown('''# 3000 Posts
analyzed for keywords''')),

                        
                        
                        ]), 

]


def find_per_match(value):
   #100,90,80,70,60,50,40,30,20,10,0
   data = [0,0,0,0,0,0,0,0,0,0,0]
   dataPie = [0,0,0,0,0,0]
   for x in counted_calcs:
      lap = set(value) & set(x[0])
      #print(f"{set(value)} doesnt overlap {set(x[0])}")
      raw = (len(lap) / len(x[0])) 
      
      if raw < 0.05:
         dataPie[5] +=x[1]
      elif raw < 0.25:
         dataPie[4] +=x[1]
      elif raw < 0.50:
         dataPie[3] +=x[1]
      elif raw < 0.75:
         dataPie[2] +=x[1]
      elif raw < 0.95:
         dataPie[1] +=x[1]
      else:
         dataPie[0] +=x[1]

      per = round(raw * 10)
      if per < 1:
         data[-1] +=x[1]
      else:
         data[-(per + 1)] += x[1]
   print(data)
   return [data, dataPie]





@callback(
   Output(component_id='match-graph',component_property='figure'),
   Output(component_id='pie-graph',component_property='figure'),
   Input(component_id='known-dropdown', component_property='value')
)
def update_match_graph(value):
   if (value is None):
      raise dash.exceptions.PreventUpdate
   matches = find_per_match(value)
   pieMatchs = matches[1]
   print(f'piematches are{pieMatchs}')
   matches = matches[0]

   matchData = pd.DataFrame(data={"Match Percentage":[100,90,80,70,60,50,40,30,20,10,0], "Market Percentage":[ round((x / listing_count) * 100) for x in  matches]})
   pieData = {"Category": ["Full Match", "75%+", "50%+", "25%+", "1%+", "Not Qualified"] , "Values":[ round((x / listing_count) * 100) for x in  pieMatchs]}

   matchFig = px.bar(matchData, x="Match Percentage", y="Market Percentage", 
                     color="Match Percentage", color_continuous_scale="Bluered_r",
                     range_color=[-10,110]
                     )
   matchFig.update_xaxes(autorange="reversed", tickmode="array", tickvals = [100,90,80,70,60,50,40,30,20,10,0], ticktext=["Full Match", "90%", "80%", "70%", "60%", "50%", "40%","30%", "20%","10%","Not Qualified" ])
   matchFig.update_yaxes( tickmode="array", tickvals = [100,90,80,70,60,50,40,30,20,10,0], ticktext=["100% of jobs", "90%", "80%", "70%", "60%", "50%", "40%","30%", "20%","10%","No Matches" ])
   matchFig.update_layout(coloraxis_showscale=False)
   matchFig.update_layout(title_text="Tech Stack vs Market")

  
   
   pieFig = px.pie(pieData, names="Category",  values="Values", 
                   labels={"Category":"Category"}, hole=.2, 
                   color_discrete_sequence=color_map_pie
                   )
   pieFig.update_layout(title_text="Tech Stack vs Market")
   pieFig.update_traces(textinfo="label")
   pieFig.update_traces(sort=False)
   

   return matchFig, pieFig


def find_top_overlap(value):
   data = {}
   for x in counted_calcs:
      overlap = set(value) & set(x[0])
      if len( overlap) > 0: # 
         for y in x[0]:
            if y not in overlap:
               if y in data:
                  data[y] +=1
               else:
                  data[y] = 0
   
   
   return data






@callback(
   Output(component_id='learn-graph',component_property='figure'),
   Input(component_id='learn_button', component_property='n_clicks'),
   State(component_id='known-dropdown', component_property='value')
   
)
def create_reccomendation(n_clicks,value):
   if (value is None):
      raise dash.exceptions.PreventUpdate
   tops = find_top_overlap(value)
   top10 = sorted(tops, key=tops.get, reverse=True)[:10]
   output = []
   for x in top10:
      output.append([x, round((tops[x]/ listing_count)*100)])
   
   upgrade_data = pd.DataFrame(data={"What you should learn": [x[0] for x in output], "Total Market Percentage Increase": [x[1]  for x in output]})
   upgrade_figure = px.bar(upgrade_data, y="Total Market Percentage Increase", x = "What you should learn")
   upgrade_figure.update_yaxes(tickmode="array", tickvals=[x for x in range(output[0][1] + 1)], ticktext = [f'{x}%' for x in range(output[0][1]+1)])
   upgrade_figure.update_layout(title_text="Best stuff to learn")

   return upgrade_figure



if __name__ == '__main__':
   app.run_server(debug=True)