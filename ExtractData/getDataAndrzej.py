import psycopg2
import time
import datetime
import commands


def GetVarArrayInterval( variable , time_start , time_end ):
    conn = psycopg2.connect(host="ifdb06.fnal.gov", user='smcreader', password='argon!smcReader',port='5438', database="slowmoncon_archive")    
    cur = conn.cursor()

    cur.execute("SELECT smpl_time,float_val FROM sample INNER JOIN channel USING (channel_id)"
        "WHERE name = %s and smpl_time > %s and smpl_time < %s;",
         (variable, time_start, time_end) )
 
    result = []
    
    for row in cur:
  #      print '| ', ' | '.join( str(v) for v in row ), ' |'
        result.append([row[0],row[1]])
        

    conn.close()
    return result  


def GetVarArrayLast( variable , time_start  ):
    conn = psycopg2.connect(host="ifdb06.fnal.gov", user='smcreader', password='argon!smcReader',port='5438', database="slowmoncon_archive")    
    cur = conn.cursor()

    cur.execute("SELECT smpl_time,float_val FROM sample INNER JOIN channel USING (channel_id)"
        "WHERE name = %s and smpl_time < %s ORDER BY smpl_time DESC LIMIT 1;",
         (variable, time_start) )
 
    result = []
    
    for row in cur:
 #       print '| ', ' | '.join( str(v) for v in row ), ' |'
        result.append([row[0],row[1]])
        

    conn.close()
    return result  



def demo():

    #-- Grab user and password
    userGrab = commands.getoutput("aescrypt -d -p $(cat pass.aes) -o - ~/.pass.txt.aes | grep smc-priv | awk '{print $2}'")
    passwordGrab  = commands.getoutput("aescrypt -d -p $(cat pass.aes) -o - ~/.pass.txt.aes | grep smc-priv | awk '{print $3}'")
    
    #-- channel name
    nameLifetime  = 'uB_ArPurity_PM02_1/LIFETIME'
    nameQC        = 'uB_ArPurity_PM02_1/CATHTRUE'
    nameQA        = 'uB_ArPurity_PM02_1/ANODETRUE'
    nameCatBase   = 'uB_ArPurity_PM02_1/CATHBASE'
    nameAnoBase   = 'uB_ArPurity_PM02_1/ANODEBASE'
    nameCathF     = 'uB_ArPurity_PM02_1/CATHFACTOR'
    nameAnoF      = 'uB_ArPurity_PM02_1/ANODEFACTOR'

    # -- Andrzej Channel names:
    
   # SELECT channel_id, name, smpl_time,num_val,float_val,str_val  FROM sample INNER JOIN channel USING (channel_id)  WHERE name = 'uB_TPCDrift_HV01_keithleyPickOff/getVoltage'  LIMIT 200;
    POPvoltage    = 'uB_TPCDrift_HV01_keithleyPickOff/getVoltage'

    AnVoltage     = 'uB_TPCDrift_HV01_keithleyCurrMon/getVoltage' 
    AnCurrent     = 'uB_TPCDrift_HV01_keithleyCurrMon/calcCurrent' 

    DigVoltage    = 'uB_TPCDrift_HV01_1_0/voltage'
    DigCurrent    = 'uB_TPCDrift_HV01_1_0/current'

    BlipFind      = 'uB_TPCDrift_HV01_keithleyPickOff/voltDiff5s60s'
    Pumpflow1     = 'uB_Cryo_IFIX_1_0/FT366'
    PumpFlow2     = 'uB_Cryo_IFIX_1_0/FT376'
   #nameLifetime 
 
    #-- get start and stop of 24-hour interval on hour boundary
    # now_hour = 3600*int(time.time()/3600)
    now_hour = time.time()
    # print now_hour

  ##### if you have the timestamp - insert it here:

    time1 = datetime.datetime.fromtimestamp(now_hour-1*60*60)
    time2 = datetime.datetime.fromtimestamp(now_hour)
    
    time3 = datetime.datetime(2015, 12, 28, 12, 30, 0 )
    time4 = datetime.datetime(2015, 12, 28, 19, 30, 0 )
    # time1 = datetime.datetime.strptime("11 18 2015 15 28 11","%m %d %Y %H %M %S")

    print 'times: ',time1,' | ',time2,' | ',time3,' | ',time4
    print 'timestamp?',time.time()
############ Pickoff Voltage 

    result = GetVarArrayInterval(POPvoltage,time3,time4)

########### access results from this array, timestamp is in [0], value in [1]

    for x in result:
        print 'out | ',x[0], ' | ',x[1],' |'

###############
#### insert other variables as needed, listed as above.


################################
###########
########### get last value of purity monitor:
###########
################################
	
    lastLife = GetVarArrayLast(nameLifetime,time2)

######### you need to unpack the date time variable + value:
    print 'lifetime | ',lastLife[0], ' |  |'
#    print 'lifetime | ',lastLife[0], ' | ',lastLife[1],' |'

#####################




#guess = "a"
#correct = "a"
#if guess == correct:
#    print "That's it!\n"

if __name__ == "__main__":
    demo()


