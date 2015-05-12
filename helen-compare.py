# -*- coding: utf-8 -*-
import json, sys, argparse
import xml.etree.ElementTree as ET
#
# Skripti vertailee Webmap-sovelluksesta haettujen kaivojen tunnusnumeroita
# työnohjausjärjestelmästä löytyviin kaivojen tunnusnumeroihin ja listaa lopulta
# työnohjausjärjestelmästä puuttuvat tunnus numerot.
#
# Tee vertailu
# python helen-compare.py -t helen-reitti-kaivot.json -w helen-reitti.xml 
#
# Tulosta helppi:
# python helen-compare.py
#
# Skripti on alun perin tehty issueta varten:
# https://jira.fifthelement.fi/browse/HELEN-480
#
# ReittiID:n selvittäminen:
# select id, external_id from route where tunnus = 'LKP1-071'; 
#
# Reitin tunnusten hakeminen tietokannasta:
# helen-kaivot-reitilta-database.py
#
# Kaivojen hakemien Webmapin rajapinnasta
# curl -X GET "http://172.26.18.102/LylyWS/ReittiWS.asmx/GetReittiTyot?Verkko=KL&ReittiID=90&Asti=20150420000000" > data.txt 
#
def load_tyonojaus_json(filename):
    with open(filename) as data_file:    
        return json.load(data_file)

def load_webmap_xml(filename):
    tree = ET.parse(filename)
    return tree.getroot()

def get_tunnus_numerot(root_element):
    tunnus_numerot = []
    tyokohteet = root_element.find('TyoKohteet')
    
    for kaivo_tag in tyokohteet.iter('Kaivo'):        
        deleted_tag = kaivo_tag.find('Poistettu')

        if deleted_tag is not None and  deleted_tag.text is not None:
            continue

        tunnus_tag = kaivo_tag.find('Tunnus')
        tunnus_numerot.append(int(tunnus_tag.text))    

    return tunnus_numerot

def map_tunnus_numerot(row):
    return row.get('target_tunnus')

def get_tunnus_numerot_json(json_data):
    return map( map_tunnus_numerot, json_data )


def create_argparser():
    parser = argparse.ArgumentParser(description='Vertailee työnohjausjärjestelmästä ja webmap:sta löytyviä tunnuksia. Skripti listaa työnohjausjärjestelmästä puuttuvat numerot.')
    parser.add_argument('-t', '--tyonohjaus', dest='tyonohjaus')
    parser.add_argument('-w', '--webmap', dest='webmap')
    return parser


def main(argv=sys.argv):

    argparser = create_argparser()

    if len(argv) == 1:
        return argparser.print_help()

    args = argparser.parse_args(argv[1:])

    root_element = load_webmap_xml(args.webmap)
    kaivon_tunnus_numerot = get_tunnus_numerot(root_element)    
    json_data = load_tyonojaus_json(args.tyonohjaus)
    ohjausjarjestelma_tunnus_numerot = get_tunnus_numerot_json(json_data)
    puuttuvat_tunnukset = [t for t in kaivon_tunnus_numerot if not t in ohjausjarjestelma_tunnus_numerot]

    print("Puuttuvien kaivojen määrä: %s" % len(puuttuvat_tunnukset) )
    print("Webmap kaivojenmäärä: %s" % len(kaivon_tunnus_numerot ) )
    print("Työnohjausjärjestelmän kaivojenmäärä: %s" % len(ohjausjarjestelma_tunnus_numerot ) )    
    print("Puuttuvat tunnukset:")

    puuttuvat_tunnukset = sorted(puuttuvat_tunnukset)

    for tunnus in puuttuvat_tunnukset:
        print( tunnus )

if __name__ == '__main__':
    main()
