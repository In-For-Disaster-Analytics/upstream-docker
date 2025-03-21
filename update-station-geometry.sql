CREATE OR REPLACE FUNCTION update_station_bounding_box(station_id_param INTEGER)
RETURNS VOID AS $$
BEGIN
    -- Update the bounding_box for the specified station
    -- by calculating the envelope of all associated measurement points
    UPDATE stations
    SET geometry = subquery.bbox
    FROM (
        SELECT
            ST_Envelope(ST_Collect(geometry)) AS bbox
        FROM
            measurements
        WHERE
            stationid = station_id_param
        GROUP BY
            stationid
    ) AS subquery
    WHERE stations.stationid = station_id_param;

    -- If no measurements exist for this station, set bounding_box to NULL
    IF NOT FOUND THEN
        UPDATE stations
        SET geometry = NULL
        WHERE stationid = station_id_param;
    END IF;
END;
$$ LANGUAGE plpgsql;



    UPDATE stations
    SET geometry = subquery.bbox
    FROM (
        SELECT
            ST_Envelope(ST_Collect(geometry))::geometry AS bbox
        FROM
            measurements
        WHERE
            stationid = 1
        GROUP BY
            stationid
    ) AS subquery
    WHERE stations.stationid = 1;


        SELECT
            ST_AsText(ST_GeomFromEWKT(ST_AsEWKT(ST_Envelope(ST_Collect(geometry))))) AS bbox
        FROM
            measurements
        WHERE
            stationid = 1
        GROUP BY
            stationid