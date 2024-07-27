from bs4 import BeautifulSoup as bs
import requests
import pandas as pd


def fetch(url):

    response = requests.get(url)
    return bs(response.text,'lxml')

def extract(web) -> dict:
    root = 'https://liquipedia.net/dota2'
    soup = fetch(web)
    area = soup.find('ul', class_='nav nav-tabs navigation-not-searchable tabs tabs6')

    team_info = {'Name':[],'Location':[],'Region':[],'Coach':[],'Total_Winnings':[]}
    links = []
    team_link = []

    #storing the page link per region
    for link in area.find_all('a',href=True):
        if link == area.find_all('a',href=True)[-1]:
            break
        links.append(link['title'])
    
    #fetching all the teams in all region
    for page in links:
        url = f'{root}/{page}'
        soup = fetch(url)
        area = soup.find_all('span', class_= 'team-template-text')

        for team in area:
            team_link.append(team.find('a',href=True)['href'])

    for team in team_link:
        url = f'https://liquipedia.net{team}'
        soup = fetch(url)
        area = soup.find('div',class_='fo-nttax-infobox')

        #get team name
        try:
            team_name = area.find('div',class_='infobox-header wiki-backgroundcolor-light').get_text()
            cleaned_name = team_name.replace('[e]', '').replace('[h]', '').strip()
            team_info['Name'].append(cleaned_name)
        except:
            team_info['Name'].append('na')
        
        #get location
        try:
            location_sibling = area.find('span',class_='flag')
            team_locatioin = location_sibling.find_next_sibling('a').get_text()
            team_info['Location'].append(team_locatioin)
        except:
            team_info['Location'].append('na')

        #get region
        try:
            regions = area.find_all('div',class_ = 'infobox-cell-2 infobox-description')

            for region in regions: 
                if region.get_text() == 'Region:':
                   region_div = region.find_next_sibling('div')
                   region_name = region_div.find_all('a')[1].get_text()
                   team_info['Region'].append(region_name)                  
        except:
            team_info['Region'].append('na')

        #get coach
        try:
            coach_name = area.find('span',class_='inline-player').find('a').get_text()
            team_info['Coach'].append(coach_name)
        except:
            team_info['Coach'].append('na')

        #get winnings $
        try:
            winning_column = area.find_all('div')
            for win in winning_column:
                if '$' in win.get_text() and 'Approx' not in win.get_text():
                    team_info['Total_Winnings'].append(win.get_text())    
        except:
            team_info['Total_Winnings'].append('na')

    return team_info


def main():
    
    web = 'https://liquipedia.net/dota2/Portal:Teams'
    print('extracting...')
    df = pd.DataFrame(extract(web))
    df.to_csv('dota2_teams.csv',index=False)
    print('done...')
        

if __name__ == "__main__":  
    main()
    