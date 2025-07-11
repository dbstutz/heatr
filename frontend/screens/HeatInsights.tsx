import React, { useEffect, useState } from 'react';
import { View, Text, TextInput, StyleSheet, ScrollView, TouchableOpacity} from 'react-native';


const Table = ({ mainEvent, athletes, navigation }) => {
    const [message, setMessage] = useState('');
    const [Stats, setStats] = useState('');
    const [selectedPR, setSelectedPR] = useState(mainEvent);

    if (!Array.isArray(athletes) || athletes.length === 0) {
      return (
          <View style={styles.container}>
              <Text style={styles.title}>No Athletes Found</Text>
          </View>
      );
    }

    const fetchMultipleAthletes = async (athletes) => {
      // Clear any old data or messages if needed
      setStats({}); // Assuming you store all athletes' PRs in state called `prs`
    
      // Fire off all fetches concurrently, but handle each response individually
      athletes.forEach(async ({ name, school }) => {
        try {
          const response = await fetch('http://127.0.0.1:8000/getsingledata', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, school }),
          });
    
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
    
          const result = await response.json();
          
          const data = result.success ? result.data : "Error in fetching athlete data";
              
          setStats((prev) => ({
            ...prev,
            [name]: data,
          }));
        } catch (error) {
          setMessage((prev) => prev + `Fetch error for ${name}: ${error.message}\n`);
        }
      });
    };

    useEffect(() => {
      fetchMultipleAthletes(athletes);
    }, []);

    const heatData = athletes.map((athlete) => {
      if (!Stats[athlete['name']]) {
        return {
          name: athlete['name'],
          loaded: false,
          pr: 'Searching...',
          prsData: [],
          rrsData: [],
        };
      }

      if (Stats[athlete['name']] == "Error in fetching athlete data") {
        return {
          name: athlete['name'],
          loaded: false,
          pr: 'Missing Profile',
          prsData: [],
          rrsData: [],
        };
      }

      const mydata = Stats[athlete['name']];

      const pr = mydata["Personal Records"].find(
        (record) => record[0] === String(selectedPR)
      );

      const prsData = mydata["Personal Records"].map(
          ([event, time, race, date]) => ({ event, time, race, date })
      );
      const rrsData = mydata["Most Recent"].map(
          ([race, date, event, time]) => ({ race, date, event, time })
      );
      const name = athlete['name']
      return {
        name: name,
        loaded: true,
        pr: pr ? pr[1] : 'PR Not Found',
        prsData: prsData,
        rrsData: rrsData,
      };
    });
  

    return (
        <View>
          <View style={styles.table}>
          {/* Header Row */}
          <View style={[styles.tableRow]}>
              <Text style={[styles.tableCell, styles.tableHeader, {flex: 1}]}>Lane</Text>
              <Text style={[styles.tableCell, styles.tableHeader, {flex: 3}]}>Athlete</Text>
              <View style={[styles.tableCell, styles.tableHeader, { flex: 2, justifyContent: 'center' }]}>
                <TextInput
                  value={selectedPR}
                  onChangeText={setSelectedPR}
                  placeholder={mainEvent}
                  placeholderTextColor="#fff"
                  style={[styles.tableCell, styles.tableHeader]}
                />
              </View>
          </View>
      
          {/* Data Rows */}
          {heatData.map((athlete, i) => (
              <TouchableOpacity key={i} onPress={() => navigation.navigate("Athlete Insights", { personalRecords: athlete.prsData, recentResults: athlete.rrsData, athName: athlete.name })} disabled={!athlete.loaded}>
                  <View style={styles.tableRow}>
                      <Text style={[styles.tableCell, {flex: 1}]}>{i+1}</Text>
                      <Text style={[styles.tableCell, {flex: 3}]}>{athlete.name}</Text>
                      <Text style={[styles.tableCell, {flex: 2}]}>{athlete.pr}</Text>
                  </View>
              </TouchableOpacity>
          ))}
          </View>
          <Text style={styles.sectionTitle}>Tap an Athlete's name to {`\n`} GET INSIGHTS!</Text>
          <Text>{message}</Text>
        </View>
    );
};

const HeatInsights = ({ route, navigation }) => {
    const { mainEvent, athletes } = route.params;

    return (
      <ScrollView
          style={styles.container}
          keyboardShouldPersistTaps="handled"
          nestedScrollEnabled={true}
      >
        <Text style={styles.title}>[ Heatr ]</Text>

        <Table
          mainEvent={mainEvent}
          athletes={athletes}
          navigation={navigation}
        />

        <View style={styles.buttonContainer}>
          <TouchableOpacity style={styles.button} onPress={() => navigation.goBack()}>
            <Text style={styles.buttonText}>Back</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    );
};

export default HeatInsights;

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
      marginBottom: 20,
    },
    subtitle: {
      fontFamily: 'Georgia',
      fontSize: 28,
      color: '#fff',
      textAlign: 'center',
      marginBottom: 10,
    },
    table: {
      borderWidth: 1,
      borderColor: '#fff',
      marginBottom: 10,
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
      paddingHorizontal: 6,
      alignItems: 'center',
    },
    tableHeader: {
      fontFamily: 'Georgia',
      flex: 1,
      paddingHorizontal: 0,
      paddingVertical: 6,
      color: '#fff',
      fontSize: 20,
      fontWeight: 'bold',
      textAlign: 'center',
    },
    tableCell: {
      fontFamily: 'Georgia',
      flex: 1,
      paddingHorizontal: 0,
      paddingVertical: 4,
      color: '#fff',
      textAlign: 'center',
    },
    sectionTitle: {
      fontFamily: 'Georgia',
      fontSize: 24,
      color: '#fff',
      marginTop: 20,
      marginBottom: 5,
      textAlign: 'center',
      fontWeight: 'bold',
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
  
