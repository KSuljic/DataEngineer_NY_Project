import os
import dash
from dash import dcc, html, ctx, Input, Output, State
import pandas as pd
import plotly.express as px
import pymongo
from datetime import datetime
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
from dash.exceptions import PreventUpdate

class NewswireData:
    '''The data that the Newswire API Dashboard uses will be loaded dynamically at times.'''
    def __init__(self):
        self.country_list={"AF":"Afghanistan","AX":"\u00c5land Islands","AL":"Albania","DZ":"Algeria","AS":"American Samoa","AD":"Andorra","AO":"Angola","AI":"Anguilla","AQ":"Antarctica","AG":"Antigua & Barbuda","AR":"Argentina","AM":"Armenia","AW":"Aruba","AU":"Australia","AT":"Austria","AZ":"Azerbaijan","BS":"Bahamas","BH":"Bahrain","BD":"Bangladesh","BB":"Barbados","BY":"Belarus","BE":"Belgium","BZ":"Belize","BJ":"Benin","BM":"Bermuda","BT":"Bhutan","BO":"Bolivia","BA":"Bosnia & Herzegovina","BW":"Botswana","BV":"Bouvet Island","BR":"Brazil","IO":"British Indian Ocean Territory","VG":"British Virgin Islands","BN":"Brunei","BG":"Bulgaria","BF":"Burkina Faso","BI":"Burundi","KH":"Cambodia","CM":"Cameroon","CA":"Canada","CV":"Cape Verde","BQ":"Caribbean Netherlands","KY":"Cayman Islands","CF":"Central African Republic","TD":"Chad","CL":"Chile","CN":"China","CX":"Christmas Island","CC":"Cocos (Keeling) Islands","CO":"Colombia","KM":"Comoros","CG":"Congo - Brazzaville","CD":"Congo - Kinshasa","CK":"Cook Islands","CR":"Costa Rica","CI":"C\u00f4te d\u2019Ivoire","HR":"Croatia","CU":"Cuba","CW":"Cura\u00e7ao","CY":"Cyprus","CZ":"Czechia","DK":"Denmark","DJ":"Djibouti","DM":"Dominica","DO":"Dominican Republic","EC":"Ecuador","EG":"Egypt","SV":"El Salvador","GQ":"Equatorial Guinea","ER":"Eritrea","EE":"Estonia","SZ":"Eswatini","ET":"Ethiopia","FK":"Falkland Islands","FO":"Faroe Islands","FJ":"Fiji","FI":"Finland","FR":"France","GF":"French Guiana","PF":"French Polynesia","TF":"French Southern Territories","GA":"Gabon","GM":"Gambia","GE":"Georgia","DE":"Germany","GH":"Ghana","GI":"Gibraltar","GR":"Greece","GL":"Greenland","GD":"Grenada","GP":"Guadeloupe","GU":"Guam","GT":"Guatemala","GG":"Guernsey","GN":"Guinea","GW":"Guinea-Bissau","GY":"Guyana","HT":"Haiti","HM":"Heard & McDonald Islands","HN":"Honduras","HK":"Hong Kong SAR China","HU":"Hungary","IS":"Iceland","IN":"India","ID":"Indonesia","IR":"Iran","IQ":"Iraq","IE":"Ireland","IM":"Isle of Man","IL":"Israel","IT":"Italy","JM":"Jamaica","JP":"Japan","JE":"Jersey","JO":"Jordan","KZ":"Kazakhstan","KE":"Kenya","KI":"Kiribati","KW":"Kuwait","KG":"Kyrgyzstan","LA":"Laos","LV":"Latvia","LB":"Lebanon","LS":"Lesotho","LR":"Liberia","LY":"Libya","LI":"Liechtenstein","LT":"Lithuania","LU":"Luxembourg","MO":"Macao SAR China","MG":"Madagascar","MW":"Malawi","MY":"Malaysia","MV":"Maldives","ML":"Mali","MT":"Malta","MH":"Marshall Islands","MQ":"Martinique","MR":"Mauritania","MU":"Mauritius","YT":"Mayotte","MX":"Mexico","FM":"Micronesia","MD":"Moldova","MC":"Monaco","MN":"Mongolia","ME":"Montenegro","MS":"Montserrat","MA":"Morocco","MZ":"Mozambique","MM":"Myanmar (Burma)","NA":"Namibia","NR":"Nauru","NP":"Nepal","NL":"Netherlands","NC":"New Caledonia","NZ":"New Zealand","NI":"Nicaragua","NE":"Niger","NG":"Nigeria","NU":"Niue","NF":"Norfolk Island","KP":"North Korea","MK":"North Macedonia","MP":"Northern Mariana Islands","NO":"Norway","OM":"Oman","PK":"Pakistan","PW":"Palau","PS":"Palestinian Territories","PA":"Panama","PG":"Papua New Guinea","PY":"Paraguay","PE":"Peru","PH":"Philippines","PN":"Pitcairn Islands","PL":"Poland","PT":"Portugal","PR":"Puerto Rico","QA":"Qatar","RE":"R\u00e9union","RO":"Romania","RU":"Russia","RW":"Rwanda","WS":"Samoa","SM":"San Marino","ST":"S\u00e3o Tom\u00e9 & Pr\u00edncipe","SA":"Saudi Arabia","SN":"Senegal","RS":"Serbia","SC":"Seychelles","SL":"Sierra Leone","SG":"Singapore","SX":"Sint Maarten","SK":"Slovakia","SI":"Slovenia","SB":"Solomon Islands","SO":"Somalia","ZA":"South Africa","GS":"South Georgia & South Sandwich Islands","KR":"South Korea","SS":"South Sudan","ES":"Spain","LK":"Sri Lanka","BL":"St. Barth\u00e9lemy","SH":"St. Helena","KN":"St. Kitts & Nevis","LC":"St. Lucia","MF":"St. Martin","PM":"St. Pierre & Miquelon","VC":"St. Vincent & Grenadines","SD":"Sudan","SR":"Suriname","SJ":"Svalbard & Jan Mayen","SE":"Sweden","CH":"Switzerland","SY":"Syria","TW":"Taiwan","TJ":"Tajikistan","TZ":"Tanzania","TH":"Thailand","TL":"Timor-Leste","TG":"Togo","TK":"Tokelau","TO":"Tonga","TT":"Trinidad & Tobago","TN":"Tunisia","TR":"Turkey","TM":"Turkmenistan","TC":"Turks & Caicos Islands","TV":"Tuvalu","UM":"U.S. Outlying Islands","VI":"U.S. Virgin Islands","UG":"Uganda","UA":"Ukraine","AE":"United Arab Emirates","GB":"United Kingdom","US":"United States","UY":"Uruguay","UZ":"Uzbekistan","VU":"Vanuatu","VA":"Vatican City","VE":"Venezuela","VN":"Vietnam","WF":"Wallis & Futuna","EH":"Western Sahara","YE":"Yemen","ZM":"Zambia","ZW":"Zimbabwe"}
        self.country_list = [i for i in self.country_list.values()]
        self.article_log = None
        self.latest = newswire.find_one(
                {"uri":{"$ne":''}},
                sort=[( 'updated_date', pymongo.DESCENDING )]
                )
        self.oldest = newswire.find_one(
                {"uri":{"$ne":''}},
                sort=[( 'updated_date', pymongo.ASCENDING )]
                )
        self.section_df = None
        self.subsection_df = None
        self.authors_df = None
        self.geo_title_df = None
        self.geo_abstract_df = None
        self.article_count = 0 #Nifty label for the number of articles we have

    def get_articles(self):
        '''Initialise the article DataFrame on first call, use it on subsequent calls.'''
        if self.article_log is None:
            self.article_log = list(newswire.find({"uri":{"$ne":''}},
                                    {"_id":0,
                                    "slug_name":0,
                                    "uri": 0,
                                    "multimedia":0}).sort("updated_date",-1))

            for i in self.article_log:
                i.update({
                    'updated_date': datetime.fromisoformat(i['updated_date']),
                    'created_date': datetime.fromisoformat(i['created_date']),
                    'published_date': datetime.fromisoformat(i['published_date']),
                    'first_published_date': datetime.fromisoformat(i['first_published_date'])
                })

        return self.article_log

    def get_authors(self):
        '''Initialise the authors DataFrame on first call, use it on subsequent calls.'''
        if self.authors_df is None:
            nb_articles_by_author = list(newswire.aggregate([
                {"$match":
                    {"byline":{"$ne":''}}
                },
                {"$project":
                    {
                        "byline":1,
                        "section":1,
                        "subsection":1,
                        "item_type":1,

                        "aYear": {"$year":
                            {"$dateFromString":{'dateString':'$created_date'}}
                        },
                        "aMonth": {"$month":
                            {"$dateFromString":{'dateString':'$created_date'}}
                        },
                        "aDay": {"$dayOfMonth":
                            {"$dateFromString":{'dateString':'$created_date'}}
                        }
                    }
                },
                {"$group":
                    {"_id":
                        {
                            "byline":"$byline",
                            "section":"$section",
                            "subsection":"$subsection",
                            "aYear":"$aYear",
                            "aMonth":"$aMonth",
                            "aDay":"$aDay"},
                            "nb_articles":{"$sum":1}
                    }
                },
                {
                    "$sort":{"nb_articles": -1, "aYear":-1, "aMonth":-1, "aDay":-1}
                },
                {"$project":
                {
                    "byline":"$_id.byline",
                    "section":"$_id.section",
                    "subsection":"$_id.subsection",
                    "year":"$_id.aYear",
                    "month":"$_id.aMonth",
                    "day":"$_id.aDay",
                    "nb_articles":1,
                    "_id":0
                }
                }
            ]))
            self.authors_df = pd.DataFrame(nb_articles_by_author)

        return self.authors_df

    def get_section_data(self):
        '''Initialise the section DataFrame (without subsections) on first call, use it on subsequent calls.'''
        if self.section_df is None:
            nb_articles_per_section = list(newswire.aggregate([
                {"$match":
                    {"uri":{"$ne":''}}
                },
                {"$project":
                    {"section":1,
                    "aYear": {"$year":
                            {"$dateFromString":{'dateString':'$created_date'}}
                        },
                    "aMonth": {"$month":
                            {"$dateFromString":{'dateString':'$created_date'}}
                        },
                    "aDay": {"$dayOfMonth":
                            {"$dateFromString":{'dateString':'$created_date'}
                        }
                }}},
                {"$group":
                    {"_id":
                        {"section":"$section",
                        "aYear":"$aYear",
                        "aMonth":"$aMonth",
                        "aDay":"$aDay"},
                    "nb_articles":{"$sum":1}}
                },
                {
                    "$sort":{"nb_articles": -1, "aYear":-1, "aMonth":-1, "aDay":-1}
                },
                {"$project":
                {
                    "section":"$_id.section",
                    "year":"$_id.aYear",
                    "month":"$_id.aMonth",
                    "day":"$_id.aDay",
                    "nb_articles":1,
                    "_id":0
                }
                }
            ]))
            self.section_df = pd.DataFrame(nb_articles_per_section)

        return self.section_df

    def get_subsection_data(self):
        '''Initialise the section DataFrame (with subsections) on first call, use it on subsequent calls.'''
        if self.subsection_df is None:
            nb_articles_per_subsection = list(newswire.aggregate([
                {"$match":
                    {"uri":{"$ne":''}}
                },
                {"$project":
                    {
                        "section":1,
                        "subsection":1,
                        "aYear": {"$year":
                            {"$dateFromString":{'dateString':'$created_date'}}
                        },
                        "aMonth": {"$month":
                            {"$dateFromString":{'dateString':'$created_date'}}
                        },
                        "aDay": {"$dayOfMonth":
                            {"$dateFromString":{'dateString':'$created_date'}}
                        }
                    }
                },
                {"$group":
                    {"_id":
                        {
                            "section":"$section",
                            "subsection":"$subsection",
                            "aYear":"$aYear",
                            "aMonth":"$aMonth",
                            "aDay":"$aDay"},
                            "nb_articles":{"$sum":1}
                    }
                },
                {
                    "$sort":{"nb_articles": -1, "aYear":-1, "aMonth":-1, "aDay":-1}
                },
                {"$project":
                {
                    "section":"$_id.section",
                    "subsection":"$_id.subsection",
                    "year":"$_id.aYear",
                    "month":"$_id.aMonth",
                    "day":"$_id.aDay",
                    "nb_articles":1,
                    "_id":0
                }
                }
            ]))
            self.subsection_df = pd.DataFrame(nb_articles_per_subsection)
            self.subsection_df = self.subsection_df.sort_values(by=['year','month','day'], ascending=False)
            self.subsection_df['Date'] = pd.to_datetime(self.subsection_df[['year','month','day']])

        return self.subsection_df

    def get_geo_data(self, type:int):
        '''Initialise the Geographical DataFrame on first call, use it on subsequent calls.'''
        if (type==0):
            if self.geo_title_df is None:
                #Credits to umpirsky for the country lists - see:
                #github.com/umpirsky/country-list/blob/master/data/en_us/country.json
                country_list = {"AF":"Afghanistan","AX":"\u00c5land Islands","AL":"Albania","DZ":"Algeria","AS":"American Samoa","AD":"Andorra","AO":"Angola","AI":"Anguilla","AQ":"Antarctica","AG":"Antigua & Barbuda","AR":"Argentina","AM":"Armenia","AW":"Aruba","AU":"Australia","AT":"Austria","AZ":"Azerbaijan","BS":"Bahamas","BH":"Bahrain","BD":"Bangladesh","BB":"Barbados","BY":"Belarus","BE":"Belgium","BZ":"Belize","BJ":"Benin","BM":"Bermuda","BT":"Bhutan","BO":"Bolivia","BA":"Bosnia & Herzegovina","BW":"Botswana","BV":"Bouvet Island","BR":"Brazil","IO":"British Indian Ocean Territory","VG":"British Virgin Islands","BN":"Brunei","BG":"Bulgaria","BF":"Burkina Faso","BI":"Burundi","KH":"Cambodia","CM":"Cameroon","CA":"Canada","CV":"Cape Verde","BQ":"Caribbean Netherlands","KY":"Cayman Islands","CF":"Central African Republic","TD":"Chad","CL":"Chile","CN":"China","CX":"Christmas Island","CC":"Cocos (Keeling) Islands","CO":"Colombia","KM":"Comoros","CG":"Congo - Brazzaville","CD":"Congo - Kinshasa","CK":"Cook Islands","CR":"Costa Rica","CI":"C\u00f4te d\u2019Ivoire","HR":"Croatia","CU":"Cuba","CW":"Cura\u00e7ao","CY":"Cyprus","CZ":"Czechia","DK":"Denmark","DJ":"Djibouti","DM":"Dominica","DO":"Dominican Republic","EC":"Ecuador","EG":"Egypt","SV":"El Salvador","GQ":"Equatorial Guinea","ER":"Eritrea","EE":"Estonia","SZ":"Eswatini","ET":"Ethiopia","FK":"Falkland Islands","FO":"Faroe Islands","FJ":"Fiji","FI":"Finland","FR":"France","GF":"French Guiana","PF":"French Polynesia","TF":"French Southern Territories","GA":"Gabon","GM":"Gambia","GE":"Georgia","DE":"Germany","GH":"Ghana","GI":"Gibraltar","GR":"Greece","GL":"Greenland","GD":"Grenada","GP":"Guadeloupe","GU":"Guam","GT":"Guatemala","GG":"Guernsey","GN":"Guinea","GW":"Guinea-Bissau","GY":"Guyana","HT":"Haiti","HM":"Heard & McDonald Islands","HN":"Honduras","HK":"Hong Kong SAR China","HU":"Hungary","IS":"Iceland","IN":"India","ID":"Indonesia","IR":"Iran","IQ":"Iraq","IE":"Ireland","IM":"Isle of Man","IL":"Israel","IT":"Italy","JM":"Jamaica","JP":"Japan","JE":"Jersey","JO":"Jordan","KZ":"Kazakhstan","KE":"Kenya","KI":"Kiribati","KW":"Kuwait","KG":"Kyrgyzstan","LA":"Laos","LV":"Latvia","LB":"Lebanon","LS":"Lesotho","LR":"Liberia","LY":"Libya","LI":"Liechtenstein","LT":"Lithuania","LU":"Luxembourg","MO":"Macao SAR China","MG":"Madagascar","MW":"Malawi","MY":"Malaysia","MV":"Maldives","ML":"Mali","MT":"Malta","MH":"Marshall Islands","MQ":"Martinique","MR":"Mauritania","MU":"Mauritius","YT":"Mayotte","MX":"Mexico","FM":"Micronesia","MD":"Moldova","MC":"Monaco","MN":"Mongolia","ME":"Montenegro","MS":"Montserrat","MA":"Morocco","MZ":"Mozambique","MM":"Myanmar (Burma)","NA":"Namibia","NR":"Nauru","NP":"Nepal","NL":"Netherlands","NC":"New Caledonia","NZ":"New Zealand","NI":"Nicaragua","NE":"Niger","NG":"Nigeria","NU":"Niue","NF":"Norfolk Island","KP":"North Korea","MK":"North Macedonia","MP":"Northern Mariana Islands","NO":"Norway","OM":"Oman","PK":"Pakistan","PW":"Palau","PS":"Palestinian Territories","PA":"Panama","PG":"Papua New Guinea","PY":"Paraguay","PE":"Peru","PH":"Philippines","PN":"Pitcairn Islands","PL":"Poland","PT":"Portugal","PR":"Puerto Rico","QA":"Qatar","RE":"R\u00e9union","RO":"Romania","RU":"Russia","RW":"Rwanda","WS":"Samoa","SM":"San Marino","ST":"S\u00e3o Tom\u00e9 & Pr\u00edncipe","SA":"Saudi Arabia","SN":"Senegal","RS":"Serbia","SC":"Seychelles","SL":"Sierra Leone","SG":"Singapore","SX":"Sint Maarten","SK":"Slovakia","SI":"Slovenia","SB":"Solomon Islands","SO":"Somalia","ZA":"South Africa","GS":"South Georgia & South Sandwich Islands","KR":"South Korea","SS":"South Sudan","ES":"Spain","LK":"Sri Lanka","BL":"St. Barth\u00e9lemy","SH":"St. Helena","KN":"St. Kitts & Nevis","LC":"St. Lucia","MF":"St. Martin","PM":"St. Pierre & Miquelon","VC":"St. Vincent & Grenadines","SD":"Sudan","SR":"Suriname","SJ":"Svalbard & Jan Mayen","SE":"Sweden","CH":"Switzerland","SY":"Syria","TW":"Taiwan","TJ":"Tajikistan","TZ":"Tanzania","TH":"Thailand","TL":"Timor-Leste","TG":"Togo","TK":"Tokelau","TO":"Tonga","TT":"Trinidad & Tobago","TN":"Tunisia","TR":"Turkey","TM":"Turkmenistan","TC":"Turks & Caicos Islands","TV":"Tuvalu","UM":"U.S. Outlying Islands","VI":"U.S. Virgin Islands","UG":"Uganda","UA":"Ukraine","AE":"United Arab Emirates","GB":"United Kingdom","US":"United States","UY":"Uruguay","UZ":"Uzbekistan","VU":"Vanuatu","VA":"Vatican City","VE":"Venezuela","VN":"Vietnam","WF":"Wallis & Futuna","EH":"Western Sahara","YE":"Yemen","ZM":"Zambia","ZW":"Zimbabwe"}
                country_list = [i for i in country_list.values()]
                country_validator = '|'.join(country_list) #Regex mask incoming!

                nb_articles_by_country_in_title = list(newswire.aggregate([
                    {"$match":
                        {"$and":
                            [{"uri":{"$ne":''}},
                            {"title":{"$regex":country_validator}}
                            ]
                        }
                    },
                    {"$project":
                        {
                            "title":{"$regexFind":
                                    {"input":"$title",
                                    "regex":country_validator}}
                            ,
                            "section":1,
                            "subsection":1,
                            "item_type":1,

                            "aYear": {"$year":
                                {"$dateFromString":{'dateString':'$created_date'}}
                            },
                            "aMonth": {"$month":
                                {"$dateFromString":{'dateString':'$created_date'}}
                            },
                            "aDay": {"$dayOfMonth":
                                {"$dateFromString":{'dateString':'$created_date'}}
                            }
                        }
                    },
                    {"$unwind":"$title"},
                    {"$group":
                        {"_id":
                            {
                                "country":"$title.match",
                                "section":"$section",
                                "aYear":"$aYear",
                                "aMonth":"$aMonth",
                                "aDay":"$aDay"},
                                "nb_articles":{"$sum":1}
                        }
                    },
                    {
                        "$sort":{"nb_articles": -1, "aYear":-1, "aMonth":-1, "aDay":-1}
                    },
                    {"$project":
                    {
                        "country":"$_id.country",
                        "section":"$_id.section",
                        "year":"$_id.aYear",
                        "month":"$_id.aMonth",
                        "day":"$_id.aDay",
                        "nb_articles":1,
                        "_id":0
                    }
                    }
                ]))
                self.geo_title_df = pd.DataFrame(nb_articles_by_country_in_title)
                self.geo_title_df = self.geo_title_df.sort_values(by=['year','month','day'], ascending=False)
                self.geo_title_df['Date'] = pd.to_datetime(self.geo_title_df[['year','month','day']])
            return self.geo_title_df
        else:
            if self.geo_abstract_df is None:
                country_list = {"AF":"Afghanistan","AX":"\u00c5land Islands","AL":"Albania","DZ":"Algeria","AS":"American Samoa","AD":"Andorra","AO":"Angola","AI":"Anguilla","AQ":"Antarctica","AG":"Antigua & Barbuda","AR":"Argentina","AM":"Armenia","AW":"Aruba","AU":"Australia","AT":"Austria","AZ":"Azerbaijan","BS":"Bahamas","BH":"Bahrain","BD":"Bangladesh","BB":"Barbados","BY":"Belarus","BE":"Belgium","BZ":"Belize","BJ":"Benin","BM":"Bermuda","BT":"Bhutan","BO":"Bolivia","BA":"Bosnia & Herzegovina","BW":"Botswana","BV":"Bouvet Island","BR":"Brazil","IO":"British Indian Ocean Territory","VG":"British Virgin Islands","BN":"Brunei","BG":"Bulgaria","BF":"Burkina Faso","BI":"Burundi","KH":"Cambodia","CM":"Cameroon","CA":"Canada","CV":"Cape Verde","BQ":"Caribbean Netherlands","KY":"Cayman Islands","CF":"Central African Republic","TD":"Chad","CL":"Chile","CN":"China","CX":"Christmas Island","CC":"Cocos (Keeling) Islands","CO":"Colombia","KM":"Comoros","CG":"Congo - Brazzaville","CD":"Congo - Kinshasa","CK":"Cook Islands","CR":"Costa Rica","CI":"C\u00f4te d\u2019Ivoire","HR":"Croatia","CU":"Cuba","CW":"Cura\u00e7ao","CY":"Cyprus","CZ":"Czechia","DK":"Denmark","DJ":"Djibouti","DM":"Dominica","DO":"Dominican Republic","EC":"Ecuador","EG":"Egypt","SV":"El Salvador","GQ":"Equatorial Guinea","ER":"Eritrea","EE":"Estonia","SZ":"Eswatini","ET":"Ethiopia","FK":"Falkland Islands","FO":"Faroe Islands","FJ":"Fiji","FI":"Finland","FR":"France","GF":"French Guiana","PF":"French Polynesia","TF":"French Southern Territories","GA":"Gabon","GM":"Gambia","GE":"Georgia","DE":"Germany","GH":"Ghana","GI":"Gibraltar","GR":"Greece","GL":"Greenland","GD":"Grenada","GP":"Guadeloupe","GU":"Guam","GT":"Guatemala","GG":"Guernsey","GN":"Guinea","GW":"Guinea-Bissau","GY":"Guyana","HT":"Haiti","HM":"Heard & McDonald Islands","HN":"Honduras","HK":"Hong Kong SAR China","HU":"Hungary","IS":"Iceland","IN":"India","ID":"Indonesia","IR":"Iran","IQ":"Iraq","IE":"Ireland","IM":"Isle of Man","IL":"Israel","IT":"Italy","JM":"Jamaica","JP":"Japan","JE":"Jersey","JO":"Jordan","KZ":"Kazakhstan","KE":"Kenya","KI":"Kiribati","KW":"Kuwait","KG":"Kyrgyzstan","LA":"Laos","LV":"Latvia","LB":"Lebanon","LS":"Lesotho","LR":"Liberia","LY":"Libya","LI":"Liechtenstein","LT":"Lithuania","LU":"Luxembourg","MO":"Macao SAR China","MG":"Madagascar","MW":"Malawi","MY":"Malaysia","MV":"Maldives","ML":"Mali","MT":"Malta","MH":"Marshall Islands","MQ":"Martinique","MR":"Mauritania","MU":"Mauritius","YT":"Mayotte","MX":"Mexico","FM":"Micronesia","MD":"Moldova","MC":"Monaco","MN":"Mongolia","ME":"Montenegro","MS":"Montserrat","MA":"Morocco","MZ":"Mozambique","MM":"Myanmar (Burma)","NA":"Namibia","NR":"Nauru","NP":"Nepal","NL":"Netherlands","NC":"New Caledonia","NZ":"New Zealand","NI":"Nicaragua","NE":"Niger","NG":"Nigeria","NU":"Niue","NF":"Norfolk Island","KP":"North Korea","MK":"North Macedonia","MP":"Northern Mariana Islands","NO":"Norway","OM":"Oman","PK":"Pakistan","PW":"Palau","PS":"Palestinian Territories","PA":"Panama","PG":"Papua New Guinea","PY":"Paraguay","PE":"Peru","PH":"Philippines","PN":"Pitcairn Islands","PL":"Poland","PT":"Portugal","PR":"Puerto Rico","QA":"Qatar","RE":"R\u00e9union","RO":"Romania","RU":"Russia","RW":"Rwanda","WS":"Samoa","SM":"San Marino","ST":"S\u00e3o Tom\u00e9 & Pr\u00edncipe","SA":"Saudi Arabia","SN":"Senegal","RS":"Serbia","SC":"Seychelles","SL":"Sierra Leone","SG":"Singapore","SX":"Sint Maarten","SK":"Slovakia","SI":"Slovenia","SB":"Solomon Islands","SO":"Somalia","ZA":"South Africa","GS":"South Georgia & South Sandwich Islands","KR":"South Korea","SS":"South Sudan","ES":"Spain","LK":"Sri Lanka","BL":"St. Barth\u00e9lemy","SH":"St. Helena","KN":"St. Kitts & Nevis","LC":"St. Lucia","MF":"St. Martin","PM":"St. Pierre & Miquelon","VC":"St. Vincent & Grenadines","SD":"Sudan","SR":"Suriname","SJ":"Svalbard & Jan Mayen","SE":"Sweden","CH":"Switzerland","SY":"Syria","TW":"Taiwan","TJ":"Tajikistan","TZ":"Tanzania","TH":"Thailand","TL":"Timor-Leste","TG":"Togo","TK":"Tokelau","TO":"Tonga","TT":"Trinidad & Tobago","TN":"Tunisia","TR":"Turkey","TM":"Turkmenistan","TC":"Turks & Caicos Islands","TV":"Tuvalu","UM":"U.S. Outlying Islands","VI":"U.S. Virgin Islands","UG":"Uganda","UA":"Ukraine","AE":"United Arab Emirates","GB":"United Kingdom","US":"United States","UY":"Uruguay","UZ":"Uzbekistan","VU":"Vanuatu","VA":"Vatican City","VE":"Venezuela","VN":"Vietnam","WF":"Wallis & Futuna","EH":"Western Sahara","YE":"Yemen","ZM":"Zambia","ZW":"Zimbabwe"}
                country_list = [i for i in country_list.values()]
                country_validator = '|'.join(country_list) #Regex mask incoming!
                nb_articles_by_country_in_abstract = list(newswire.aggregate([
                    {"$match":
                        {"$and":
                            [{"uri":{"$ne":''}},
                            {"abstract":{"$regex":country_validator}}
                            ]
                        }
                    },
                    {"$project":
                        {
                            "abstract":{"$regexFind":
                                    {"input":"$abstract",
                                    "regex":country_validator}}
                            ,
                            "section":1,
                            "subsection":1,
                            "item_type":1,

                            "aYear": {"$year":
                                {"$dateFromString":{'dateString':'$created_date'}}
                            },
                            "aMonth": {"$month":
                                {"$dateFromString":{'dateString':'$created_date'}}
                            },
                            "aDay": {"$dayOfMonth":
                                {"$dateFromString":{'dateString':'$created_date'}}
                            }
                        }
                    },
                    {"$unwind":"$abstract"},
                    {"$group":
                        {"_id":
                            {
                                "country":"$abstract.match",
                                "section":"$section",
                                "aYear":"$aYear",
                                "aMonth":"$aMonth",
                                "aDay":"$aDay"},
                                "nb_articles":{"$sum":1}
                        }
                    },
                    {
                        "$sort":{"nb_articles": -1, "aYear":-1, "aMonth":-1, "aDay":-1}
                    },
                    {"$project":
                    {
                        "country":"$_id.country",
                        "section":"$_id.section",
                        "year":"$_id.aYear",
                        "month":"$_id.aMonth",
                        "day":"$_id.aDay",
                        "nb_articles":1,
                        "_id":0
                    }
                    }
                ]))
                self.geo_abstract_df = pd.DataFrame(nb_articles_by_country_in_abstract)
                self.geo_abstract_df['Date'] = pd.to_datetime(self.geo_abstract_df[['year','month','day']])

            return self.geo_abstract_df

#Receiving our data from MongoDB
MONGO_LABEL = os.environ.get('MONGODB_ADDRESS','localhost') #Unless you have your own address
MONGO_PORT = int(os.environ.get('MONGODB_PORT',27017)) #Unless you have a specific port, default is 27017
DB_CLIENT = pymongo.MongoClient('mongodb', 27017) # pymongo.MongoClient(host=MONGO_LABEL, port=MONGO_PORT)
db = DB_CLIENT['NY_Project']

#Nonfiction books will have a standalone API, courtesy of Jessica.
#TO_DO: insert code here
articlesearch = db['ny_articles'] #Kenan's NY Articles Collection
newswire = db['times_newswire'] #I moved mine to Kenan's db, but the collections are distinct from one another

nwdata = NewswireData()

#Loading the values that go into the section dropdown on the Topic tab - Newswire API Data
section_labels = ['All']
section_labels.extend(newswire.distinct('section'))
#section_labels.remove('')

nw_search_res = []
nw_search_size = 10

#Article Search Section
pipeline = [
    {
        '$group': {
            '_id': '$news_desk',
            # 'section_word_count': {'$sum': '$word_count'},
            'section_word_count': {'$avg': '$word_count'},
            'section_article_count': {'$sum': 1},
            'newest_articles': {
                '$push': {
                    'headline': '$headline',
                    'web_url': '$web_url',
                    'pub_date': '$pub_date'
                }
            }
        }
    },
    {
        '$group': {
            '_id': None,
            'average_word_count': {'$avg': '$section_word_count'},
            'total_article_count': {'$sum': '$section_article_count'},
            'sections': {
                '$push': {
                    'section': '$_id',
                    'average_word_count': {'$avg': '$section_word_count'},
                    'article_count': '$section_article_count'
                }
            },
            'all_articles': {'$push': '$newest_articles'}
        }
    },
    {
        '$project': {
            'average_word_count': 1,
            'total_article_count': 1,
            'sections': 1,
            # Flatten the array of arrays
            'flattened_articles': {'$reduce': {
                'input': '$all_articles',
                'initialValue': [],
                'in': {'$concatArrays': ['$$value', '$$this']}
            }}
        }
    },
    {
        '$unwind': '$flattened_articles'
    },
    {
        '$sort': {'flattened_articles.pub_date': -1}
    },
    {
        '$limit': 5
    },
    {
        '$group': {
            '_id': '$_id',
            'average_word_count': {'$first': '$average_word_count'},
            'total_article_count': {'$first': '$total_article_count'},
            'sections': {'$first': '$sections'},
            'newest_articles': {'$push': '$flattened_articles'}
        }
    }
]

result_article_search = list(articlesearch.aggregate(pipeline))

if result_article_search:
   # Extracting data from the 'result' for 'sections'
    sections_data = [    {'section': section['section'], 'count': section['article_count']}
        for section in result_article_search[0]['sections']
    ]

    # # Save aggregated data into a new collection
    # aggregated_data_collection = db.ny_articles_aggregated_data
    # aggregated_data_collection.insert_one({
    #     'total_articles': sum(section['count'] for section in sections_data),
    #     'average_word_count': result[0]['average_word_count'],
    #     'sections': sections_data,
    #     'newest_articles': result[0]['newest_articles'],
    #     'timestamp': datetime.now()
    # })

    # # Extract total number of articles, average word count, sections with counts, and newest articles
    total_articles = result_article_search[0]["total_article_count"]
    average_word_count = result_article_search[0]["average_word_count"]
    sections = [section['section'] for section in result_article_search[0]['sections']]
    article_counts = [section['article_count'] for section in result_article_search[0]['sections']]
    newest_articles = result_article_search[0]['newest_articles']

    ## Figure
    # Extract the data for the scatter plot
    scatter_data = result_article_search[0]['sections']

#Theme loaded: SLATE. Can change.
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SLATE], suppress_callback_exceptions=True)
load_figure_template('slate')

#Article search: Plotly
# Create a scatter plot using Plotly Express
fig_article = px.scatter(
    scatter_data,
    x='article_count',
    y='average_word_count',
    text='section',
    labels={'article_count': 'Number of Articles', 'average_word_count': 'Average Word Count'},
    color='section',
    title='Number of Articles vs Average Word Count per Section',
    template='plotly_dark'
)
fig_article.update_layout(
        {
            "paper_bgcolor": "rgba(0, 0, 0, 0)",
            "plot_bgcolor": "rgba(0, 0, 0, 0)",
        }
    )

# Scatter plot showing number of articles vs average word count per section
scatter_plot = dcc.Graph(
    id='section-scatter-plot',
    figure=fig_article,
    config={'displayModeBar': False}  # Hide the interactive mode bar
)

#Sidebar and main page implementations taken from DBC's documentation
sidebar_style = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
}
content_style = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}
sidebar = html.Div(
    [
        html.H2("NY News Project", className="display-4"),
        html.Hr(),
        html.P(
            "The New York Times at a Glance", className="lead"
        ),
        dbc.Nav(
            [
                dbc.NavLink("Home", href="/", active="exact"),
                dbc.NavLink("Articles", href="/articles", active="exact"),
                #dbc.NavLink("Books", href="/books", active="exact"), Not implemented yet
                dbc.NavLink("Newswire", href="/newswire", active="exact")
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style = sidebar_style
)

#Overall page layout, do not modify
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    sidebar,
    html.Div(id = 'page-content', style=content_style)
])

#App title
app.title = 'NYT Newswire API Dashboard'

#Landing page
index_page = html.Div([
    html.H1('The New York Times as seen by three distinct APIs.'),
    html.Br(),
    dcc.Markdown("""The New York Times' wealth of information can be difficult to sift through, especially when the outlet publishes 100 articles per day on average. In this context, some news may fall through the cracks.

If that was not problematic enough, given the amount of nonfiction book releases, books of potential interest will fall through the cracks be it in the news cycle or due to daily life events.

Our project goes beyond covering those aspects as it makes an effort to look through news cycle related trends, using the Times' [publicly available IT resources.](https://developer.nytimes.com/)""",
link_target='_blank') #Opens a new tab if someone clicks on the NYT API Portal link.
])

tab_nw_search = html.Div([
    html.H2('Search for articles'),
    html.Div([dcc.Input(
        placeholder='Enter your search query here...',
        type='text',
        value='',
        id='searchText'),
        html.Button('Search', id='searchButton'),
        dbc.Pagination(min_value = 1, max_value=1, first_last=True, previous_next=True,
                       fully_expanded=False,
                       id='searchResPage')]),
    html.Br(),
    html.Div([dcc.Markdown(
        #blank_df.to_dict('records'),
        id='searchResultsLog',
        link_target='_blank')],
        id='mdSearchContent')
])

tab_nw_topic = html.Div([
    html.H2('NYT Stats by topic'),
    html.Div([
        dcc.Dropdown(section_labels,None,id='sectionDrop'),
        dcc.Dropdown(['All'],'All',id='subsectionDrop')
    ]),
    html.Br(),
    html.Div(id='graphArea')
])

tab_nw_geo = html.Div([
    html.H2('NYT Stats by countries mentioned'),
    html.Div(
        dbc.Row([
            dbc.Col(dcc.RadioItems(options=['In the title','In the article'],value=None,id='countryMode')),
            dbc.Col(html.Div(["You can also choose a section here",
                dcc.Dropdown(['All'],'All',id='sectionDropCountry')]
                ))
    ])),
    html.Br(),
    dcc.Markdown('Once a choice is made between **title** and **article** content (right above), be prepared to wait a little as graphs take time to generate.'),
    html.Br(),
    html.Div(id='graphAreaCountry')
])

layout_books = html.Div() #Insert Jessica's section here

tab_art_landing = html.Div([
    html.H2(children='NY Times Article Statistics'),
    html.Div(children=f'Total articles: {total_articles}', style={'marginBottom': 20}),
    html.Div(children=f'The average word count is: {average_word_count:.2f}', style={'marginBottom': 20}),
    html.Br(),
    html.H2("5 Latest Articles:"),
    # Create a list of links to the 5 newest articles
    html.Ul([
        html.Li(html.A(article['headline']['main'], href=article['web_url'],target='_blank'), style={'list-style-type': 'none'}) for article in newest_articles
    ])]
    )

tab_art_graph = html.Div([
    html.H2("Scatter Plot: Number of Articles vs Average Word Count per Section"),
    scatter_plot
    ])

tab_art_sections_detailed = html.Div([
    html.H2("Articles per Section:"),
    html.Br(),
    # Create a list of sections and counts
    html.Ul([
        html.Li(f"{section}: {count} articles") for section, count in zip(sections, article_counts)
    ])
])

tab_art_search = html.Div(children=[

    # Search bar
    html.H2("Article Search"),
    dcc.Input(id='search-input', type='text', placeholder='Enter keywords...'),

    # Create a list of links to the articles based on the search results
    html.Ul(id='search-results')

])

article_tabs = dbc.Tabs([
    dbc.Tab([tab_art_landing, tab_art_search], label='Articles at a Glance'),
    dbc.Tab(tab_art_graph, label='Word Count Distribution Per Section'),
    dbc.Tab(tab_art_sections_detailed, label='More Section Info')
])

layout_articles = html.Div([article_tabs])

# Define callback to update search results
@app.callback(
    Output('search-results', 'children'),
    [Input('search-input', 'value')],
    prevent_initial_call=True
)
def update_search_results(search_query):
    # MongoDB query to find articles containing the search query in keywords
    search_pipeline = [
        {'$match': {'keywords.value': {'$regex': f'{search_query}', '$options': 'i'}}},
        {'$project': {'headline': '$headline.main', 'web_url': '$web_url', '_id': 0}},
        {'$limit': 5}
    ]

    search_results = list(articlesearch.aggregate(search_pipeline))

    # Display search results as links
    result_links = [
        html.Li(html.A(result['headline'], href=result['web_url'], target='_blank')) for result in search_results
    ]

    return result_links #Insert Kenan's section here

newswire_tabs = dbc.Tabs([
    dbc.Tab(tab_nw_search, label='Search for articles'),
    dbc.Tab(tab_nw_topic, label='NY Times stats: Sections'),
    dbc.Tab(tab_nw_geo, label='NY Times stats: Geographical mentions')
])

layout_newswire = html.Div([newswire_tabs])

#The navigation bar is the only feature that should change this.
@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    global nw_search_res

    #If we're switching away from the Newswire tab, we clear the Newswire's searches.
    #Reason: clunky stuff happens without this part. It's funny and harmless, but yeah.
    if pathname != 'newswire':
        nw_search_res = []

    #Managing sidebar navigation proper: different layouts for different apps.
    if pathname == '/articles':
        article_tabs.active_tab = 'tab-0'
        return layout_articles
    elif pathname == '/books':
        return layout_books
    elif pathname == '/newswire':
        newswire_tabs.active_tab = 'tab-0'
        return layout_newswire
    else:
        return index_page

#Search for entries and manage how results look (this was pure pain to implement)
@app.callback(
        dash.dependencies.Output('searchResultsLog', "children"),
        dash.dependencies.Output('searchResPage','active_page'),
        dash.dependencies.Output('searchResPage','max_value'),
        dash.dependencies.Input('searchButton','n_clicks'),
        dash.dependencies.Input('searchResPage','active_page'),
        dash.dependencies.Input('searchResPage','max_value'),
        dash.dependencies.State('searchText','value'),
        prevent_initial_call = True)
def get_search_results_newswire(pressed, page_nr, max_nr, search_term):
        '''This callback manages search results via the Newswire API in two ways:
        - Users enter their search term then press 'Search'
        - After obtaining their search results, users want to see older results
        Due to Dash's limitations, both have to be handled in the same callback.'''
        global nw_search_res
        global nw_search_size

        #What is initiating the callback? The button, or the search results' page bar?
        trigger = ctx.triggered_id

        #Case #1: We already have results, but a user is handling the page bar.
        if 'searchResPage' in trigger:

            #Did someone randomly click on the page bar when we didn't do a search at all?
            #That's fine and all, but we don't have anything to show or change.
            if len(nw_search_res) == 0:
                return '',page_nr,max_nr

            #Setting the limits of our range:
            entry_start = (page_nr-1) * nw_search_size
            entry_end = (page_nr) * nw_search_size

            #If the maximum for that page goes beyond the amount of articles for that page, we bring it back to the max.
            entry_end = len(nw_search_res) if entry_end > len(nw_search_res) else entry_end

            #Preparing our results (this is Markdown)
            txt = f'#### Showing {entry_end-entry_start} articles out of {len(nw_search_res)}:\n\n'
            for res in nw_search_res[entry_start:entry_end]:
                txt = txt+f'''

* **[{res.get("title")}]({res.get("url")})**
*Latest update: {res.get("updated_date").strftime("%m/%d/%Y, %H:%M:%S")}*
{res.get("abstract")}

'''
            return txt, page_nr, max_nr #the page number and max number of pages does not change.

        #Case #2: We are performing a new search.
        else:

            if search_term in ['',None] or pressed in [0,None]:
                raise PreventUpdate('Please insert data.')
            else:
                txt = ''
                results = nwdata.get_articles()
                nw_search_res = [i for i in results if (i.get('title','').lower().find(search_term.lower()) != -1
                                                or i.get('abstract','').lower().find(search_term.lower()) != -1)]
                if len(nw_search_res) != 0:
                    res_nr = len(nw_search_res)


                    show_max = res_nr if res_nr <= nw_search_size else nw_search_size
                    pg = res_nr // nw_search_size

                    if len(nw_search_res) % nw_search_size > 0:
                        pg = pg + 1
                    txt = txt+f'#### Showing {show_max} articles out of {res_nr}:\n\n'
                    for res in nw_search_res[0:show_max]:
                        txt = txt+f'''

* **[{res.get("title")}]({res.get("url")})**
*Latest update: {res.get("updated_date").strftime("%m/%d/%Y, %H:%M:%S")}*
{res.get("abstract")}

    '''

                else:
                    txt = 'No results found.'
                    pg = 1

                nb_pages = pg
                return txt, 1, nb_pages

#Load the subsections
@app.callback(
    dash.dependencies.Output('subsectionDrop', "options"),
    dash.dependencies.Output('subsectionDrop', "value"),
    dash.dependencies.Input('sectionDrop','value'),
    prevent_initial_call = True
)
def load_subsections(section):
    if section == 'All' or section is None:
        return ['All'],'All'
    else:
        my_df = nwdata.get_subsection_data()
        my_df = my_df[my_df.section==section]
        sub_options = ['All']
        sub_options.extend(sorted(my_df.subsection.unique()))
        sub_options[sub_options.index('')] = 'N/A'
        return sub_options,'All'

#Organize data by topic
@app.callback(
    dash.dependencies.Output('graphArea', "children"),
    [dash.dependencies.Input('sectionDrop','value'),
    dash.dependencies.Input('subsectionDrop','value')],
    prevent_initial_call = True
)
def filter_graph_subsections(section,subsection):
    my_df = nwdata.get_subsection_data()
    my_title = 'Timeline: Articles published across'

    if section is None:
        section = 'All'
    #Filtering the data
    if section != 'All':

        my_title = my_title+f' the {section} vertical'
        my_df = my_df[my_df.section == section]
        if subsection != 'All':
            if subsection == 'N/A':
                sbsval = ''
                my_title = my_title+f', without a subcategory'
            else:
                sbsval = subsection
                my_title = my_title+f', in the {sbsval} subcategory'

            my_df = my_df[my_df.subsection == sbsval]

    else:
        my_title = my_title+' all sections'

    my_df = my_df.groupby(by=['Date']).sum(numeric_only=True).reset_index(drop=False)
    my_df['Date'] = my_df['Date'].dt.strftime('%Y-%m-%d')
    fig = px.line(my_df,x='Date',y='nb_articles',title=my_title,template='plotly_dark')
    fig.update_layout(xaxis_title='Date',yaxis_title='Number of published articles')

    #Transparent background hooray!
    fig.update_layout(
        {
            "paper_bgcolor": "rgba(0, 0, 0, 0)",
            "plot_bgcolor": "rgba(0, 0, 0, 0)",
        }
    )
    return [dcc.Graph(id='topicGraph',figure=fig)]

#Change the section dropdown values in the country field depending on what we're choosing
@app.callback(
    dash.dependencies.Output('sectionDropCountry', "options"),
    dash.dependencies.Output('sectionDropCountry', "value"),
    dash.dependencies.Input('countryMode','value'),
    prevent_initial_call = True
)
def section_update_by_mode(mode):
    my_df = None
    if mode == 'In the title':
        my_df = nwdata.get_geo_data(0)
    elif mode == 'In the article':
        my_df = nwdata.get_geo_data(1)

    sub_options = ['All']
    if my_df is not None:
        sub_options.extend(sorted(my_df.section.unique()))

    return sub_options,'All'

#Organize data by country and section (if section restrictions apply)
@app.callback(
    dash.dependencies.Output('graphAreaCountry', "children"),
    [dash.dependencies.Input('countryMode','value'),
     dash.dependencies.Input('sectionDropCountry','value')],
    prevent_initial_call = True
)
def filter_graph_countries(mode,section):
    if mode is None:
        return None

    my_title = ''
    if mode == 'In the title':
        my_df = nwdata.get_geo_data(0)
        my_title = 'Timeline: Articles highlighting countries in the title'
    elif mode == 'In the article':
        my_df = nwdata.get_geo_data(1)
        my_title = 'Timeline: Articles mentioning countries in their content'

    if section is None:
        section = 'All'
    #Filtering the data
    if section != 'All':

        my_title = my_title+f' from the {section} vertical'
        my_df = my_df[my_df.section == section]

    my_df = my_df.groupby(by=['country','Date']).sum(numeric_only=True).reset_index(drop=False)
    my_df['Date'] = my_df['Date'].dt.strftime('%Y-%m-%d')


    fig = px.line(my_df,x='Date',y='nb_articles',color='country',title=my_title,template='plotly_dark')
    fig.update_layout(xaxis_title='Date',yaxis_title='Number of published articles')
    #Transparent background hooray! (again)
    fig.update_layout(
        {
            "paper_bgcolor": "rgba(0, 0, 0, 0)",
            "plot_bgcolor": "rgba(0, 0, 0, 0)",
        }
    )

    return [dcc.Graph(id='topicGraph',figure=fig)]

if __name__ == '__main__':
    app.run_server(debug=True,host="0.0.0.0")