import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity} from 'react-native';
import { get } from 'react-native/Libraries/TurboModule/TurboModuleRegistry';

const Table = ({ headers, data }) => (
    <View style={styles.table}>
      {/* Header Row */}
      <View style={[styles.row, styles.tableRow]}>
        {headers.map((header, i) => (
          <Text key={i} style={[styles.tableCell, styles.tableHeader]}>
            {header}
          </Text>
        ))}
      </View>
  
      {/* Data Rows */}
      {data.map((row, i) => (
        <View key={i} style={styles.tableRow}>
          {row.map((cell, j) => (
            <Text key={j} style={styles.tableCell}>{cell}</Text>
          ))}
        </View>
      ))}
    </View>
  );

const AthleteInsights = ({ route, navigation }: { route: any; navigation: any }) => {
    const { personalRecords, recentResults, athName } = route.params;
    const [message, setMessage] = useState('');

    const personalData = personalRecords.map(pr => [
        pr.event,
        pr.time,
        pr.race,
        pr.date,
    ]);
    
    const getInsights = async () => {
      setMessage("Generating insights...");
      const response = await fetch('http://127.0.0.1:8000/getinsights', {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          athName: athName,
          personalRecords: personalRecords
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const result = await response.json();

      if (!result.success) {
        setMessage("Error: " + result.error)
        return;
      }

      const data = result.data;

      setMessage(data);
    }

    // Call getInsights only once when the component mounts
    useEffect(() => {
      getInsights();
    }, []); // Empty dependency array ensures it runs only once


    return (
      <ScrollView style={styles.container}>
          <Text style={styles.title}>[ Heatr ]</Text>

          <Text style={styles.subtitle}>{`${athName} Insights`}</Text>
          <Table
            headers={['Event', 'PR', 'Race', 'Date']}
            data={personalData}
          />

          <Text style={styles.sectionTitle}>Latest Results:</Text>
          {recentResults.map((res, index) => (
            <Text key={index} style={styles.bullet}>{`- ${res.time} in the ${res.event} on ${res.date} at ${res.race}`}</Text>
        ))}

          <Text style={styles.sectionTitle}>AI Summary:</Text>
            <Text style={styles.summaryText}>
              {message}
            </Text>
            <View style={styles.buttonContainer}>
            <TouchableOpacity style={styles.button} onPress={() => navigation.goBack()}>
            <Text style={styles.buttonText}>Back</Text>
            </TouchableOpacity>
            </View>
      </ScrollView>
    );
};

export default AthleteInsights;

const styles = StyleSheet.create({
    container: {
      padding: 30,
      backgroundColor: '#2d2f2f',
      flex: 1,
    },
    title: {
      fontFamily: 'Georgia',
      fontSize: 28,
      color: '#fff',
      textAlign: 'center',
      marginTop: 40,
      marginBottom: 10,
    },
    subtitle: {
      fontFamily: 'Georgia',
      fontSize: 28,
      fontWeight: 'bold',
      color: '#fff',
      textAlign: 'center',
      marginBottom: 10,
    },
    table: {
      borderWidth: 1,
      borderColor: '#fff',
      marginBottom: 5,
    },
    tableRowHeader: {
      flexDirection: 'row',
      backgroundColor: '#444',
    },
    tableRow: {
      flexDirection: 'row',
      borderTopWidth: 1,
      borderColor: '#fff',
      paddingVertical: 4,
      paddingHorizontal: 4,
      alignItems: 'center',
    },
    tableHeader: {
      fontFamily: 'Georgia',
      flex: 1,
      padding: 8,
      color: '#fff',
      fontSize: 20,
      fontWeight: 'bold',
      textAlign: 'center',
    },
    tableCell: {
      fontFamily: 'Georgia',
      flex: 1,
      padding: 4,
      color: '#fff',
      textAlign: 'center',
    },
    sectionTitle: {
      fontFamily: 'Georgia',
      fontSize: 28,
      fontWeight: 'bold',
      color: '#fff',
      marginTop: 20,
      marginBottom: 5,
    },
    bullet: {
      fontFamily: 'Georgia',
      fontSize: 16,
      color: '#fff',
      marginLeft: 10,
      marginBottom: 5,
    },
    summaryText: {
      fontFamily: 'Georgia',
      fontSize: 16,
      color: '#fff',
      marginTop: 10,
    },
    buttonContainer: {
      flexDirection: 'row',
      justifyContent: 'space-evenly',
      marginTop: 20,
      marginBottom: 20,
    },
    button: {
      paddingVertical: 5,
      paddingHorizontal: 30,
      borderColor: '#fff',
      borderWidth: 3,
      borderRadius: 0,
    },
    buttonText: {
      fontFamily: 'Georgia',
      color: '#fff',
      fontSize: 20,
    },
  });
  
