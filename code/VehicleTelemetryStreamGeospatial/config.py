from email.base64mime import header_length

class BaseConfig(object):

    ################################################################################
    #
    # Baseline Configuration
    #
    ################################################################################
    
    # Database connection string - Configure with your details
    DRIVER = 'ODBC Driver 18 for SQL Server'
    SERVER_LOCAL = '(local)'    
    DATABASE = 'VehicleTelemetryDM'    
    USN=''        
    PWD=''

    ################################################################################
    #
    # OpenRouteService API
    #
    ################################################################################
    
    # OpenRouteService Access Token
    ORS_API_KEY = ''

    