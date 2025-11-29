select
    trip_id,
    started_at,
    ended_at,

    case 
        when user_type = 'Subscriber' then 'Subscriber'
        when user_type = 'Customer' then 'Casual'
        else user_type
    end as user_type_clean
from read_csv_auto('data/bikeshare_data/*.csv')
