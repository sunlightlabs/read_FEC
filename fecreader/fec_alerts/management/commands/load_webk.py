# This isn't actually the webk file it's the candiddate and committee report summary file. 

import csv
from decimal import *
from dateutil.parser import parse as dateparse

from django.core.management.base import BaseCommand
from parsing.read_FEC_settings import FTP_DATA_DIR, CYCLE
from fec_alerts.models import WebK


two_digit_cycle = "14"
#override
CYCLE = 2014

def currency_to_decimal(currency_string):
    if currency_string:
        currency_string = currency_string.replace("$","")
        currency_string = currency_string.replace(",","")
        value = None
        try:
            value = float(currency_string)
            value = Decimal(value)
        except ValueError:
            pass
        return value
    else:
        return None

# these columns are formatted like '$2,333.67' in the download, so need cleaning before entry. They're also saved as decimal. postgres does have a money type, but it's more trouble than it's worth. 
monetary_columns = ['ind_ite_con', 'ind_uni_con', 'ind_con', 'ind_ref', 'par_com_con', 'oth_com_con', 'oth_com_ref', 'can_con', 'tot_con', 'tot_con_ref', 'can_loa', 'can_loa_rep', 'oth_loa', 'oth_loa_rep', 'tot_loa', 'tot_loa_rep', 'tra_fro_oth_aut_com', 'tra_fro_non_fed_acc', 'tra_fro_non_fed_lev_acc', 'tot_non_fed_tra', 'oth_rec', 'tot_rec', 'tot_fed_rec', 'ope_exp', 'sha_fed_ope_exp', 'sha_non_fed_ope_exp', 'tot_ope_exp', 'off_to_ope_exp', 'fed_sha_of_joi_act', 'non_fed_sha_of_joi_act', 'non_all_fed_ele_act_par', 'tot_fed_ele_act', 'fed_can_com_con', 'fed_can_con_ref', 'ind_exp_mad', 'coo_exp_par', 'loa_mad', 'loa_rep_rec', 'tra_to_oth_aut_com', 'fun_dis', 'off_to_fun_exp_pre', 'exe_leg_acc_dis_pre', 'off_to_leg_acc_exp_pre', 'tot_off_to_ope_exp', 'oth_dis', 'tot_fed_dis', 'tot_dis', 'net_con', 'net_ope_exp', 'cas_on_han_beg_of_per', 'cas_on_han_clo_of_per', 'deb_owe_by_com', 'deb_owe_to_com', 'pol_par_com_ref', 'cas_on_han_beg_of_yea', 'cas_on_han_clo_of_yea', 'exp_sub_to_lim_pri_yea_pre', 'exp_sub_lim', 'fed_fun', 'ite_con_exp_con_com', 'ite_oth_dis', 'ite_oth_inc', 'ite_oth_ref_or_reb', 'ite_ref_or_reb', 'oth_fed_ope_exp', 'sub_con_exp', 'sub_oth_ref_or_reb', 'sub_ref_or_reb', 'tot_com_cos', 'tot_exp_sub_to_lim_pre', 'uni_con_exp', 'uni_oth_dis', 'uni_oth_inc', 'uni_oth_ref_or_reb', 'uni_ref_or_reb']

def readfile(filelocation):
    fh = open(filelocation, 'r')
    reader = csv.DictReader(fh)
    count = 0
    for row in reader:
    
        #print "handling %s (%s) %s to %s" % (row['com_nam'], row['com_id'], row['cov_sta_dat'], row['cov_end_dat'])
        row['cycle'] = str(CYCLE)
        try:
            row['coverage_through_date'] = dateparse(row['cov_end_dat'])
        except ValueError:
            pass
            
        try:
            row['coverage_from_date'] = dateparse(row['cov_sta_dat'])
        except ValueError:
            pass
            
        for colname in monetary_columns:
            row[colname] = currency_to_decimal(row[colname])
        # trailing comma creates nameless entry; remove it.
        try:
            del row['']
        except KeyError:
            pass
        
        try:
            thiswebk = WebK.objects.get(cycle=CYCLE, com_id=row['com_id'], cov_sta_dat=row['cov_sta_dat'], cov_end_dat=row['cov_end_dat'])
            
            # We think this file gets updated with amendments--assuming it does, put in the new values. 
            for key in row:
                setattr(thiswebk, key, row[key]) 
            thiswebk.save()
            
        except WebK.DoesNotExist:
            
            count += 1
            thiswebk = WebK(**row)
            thiswebk.save()
    print "Inserted %s new rows from file %s" % (count, filelocation)
    
class Command(BaseCommand): 
    def handle(self, *args, **options):
        print "load data from the webk file--now downloaded from the data catalog."
        
        for datatype in ['HOUSE_SENATE', 'INDEPENDENT_EXPENDITURE', 'PAC', 'PARTY', 'PRESIDENTIAL']:
            print "Handling %s data" % (datatype)
            filename =  "/%s/ccsummary_%s%s.csv" % (two_digit_cycle, datatype, two_digit_cycle)
            filelocation = FTP_DATA_DIR + filename
            readfile(filelocation)
        
