import React, { useState } from 'react';
import { StyleSheet, Text, View, StatusBar, useColorScheme, TextInput, TouchableOpacity, Image } from 'react-native';
import { launchImageLibrary } from 'react-native-image-picker';



const HomeScreen = ({ navigation }: { navigation: any }) => {
    const [message, setMessage] = useState('');
    const [name, setName] = React.useState('');
    const [school, setSchool] = React.useState('');
    const [mainEvent, setMainEvent] = React.useState('');
    const [imageUri, setImageUri] = useState<string | null>(null);
    const isDarkMode = useColorScheme() === 'dark';
  
    const fetchData = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/getsingledata', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            name,
            school,
          }),
        });
  
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const result = await response.json();

        if (!result.success) {
          setMessage("Error: " + result.error)
          return;
        }

        const data = result.data;

        const personalRecords = data["Personal Records"].map(
          ([event, time, race, date]) => ({ event, time, race, date })
        );

        const recentResults = data["Most Recent"].map(
          ([race, date, event, time]) => ({ race, date, event, time })
        );

        const athName = data['Name']

        const athletes = [data, data];
        navigation.navigate("Heat Insights", { mainEvent, athletes });

      } catch (error) {
        console.error('Error fetching data:', error);
        setMessage(`Error: ${error.message}`);
      }
    };

    const handleImageUpload = async () => {
      if (!mainEvent) {
        setMessage('Please enter event before uploading image.');
        return;
      }
      try {
        const result = await launchImageLibrary({ mediaType: 'photo' });

        if (result && result.assets) {
          const selectedImage = result.assets[0];
          setImageUri(selectedImage.uri);

          const formData = new FormData();
          formData.append('file', {
            uri: selectedImage.uri, // Use the selected image URI
            name: 'photo.jpg', // Provide a name for the file
            type: selectedImage.type || 'image/jpeg', // Use the file type from the picker
          });
    
          setMessage("Scanning image...")

          const response = await fetch('http://127.0.0.1:8000/imagescanonly', {
            method: 'POST',
            body: formData, // Attach the FormData
          });
          
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }

          const result2 = await response.json();

          const athletes = result2.data;

          setMessage("")
          
          navigation.navigate("Heat Insights", { mainEvent, athletes });
          
        } else {
          setMessage('No image selected');
        }

      } catch (error) {
        console.error('Error uploading image:', error);
        setMessage(`Error: ${error.message}`);
      }
    };
  
    return (
      <View style={[styles.container]}>
        <StatusBar barStyle={isDarkMode ? 'light-content' : 'dark-content'} />

        <Text style={styles.title}>[ Heatr ]</Text>

        {/* <TextInput
          style={styles.input}
          placeholder="Enter name"
          placeholderTextColor="#fff"
          value={name}
          onChangeText={setName}
        />

        <TextInput
          style={styles.input}
          placeholder="Enter school"
          placeholderTextColor="#fff"
          value={school}
          onChangeText={setSchool}
        />

        <View style={styles.buttonContainer}>
            <TouchableOpacity style={styles.button} onPress={fetchData}>
            <Text style={styles.buttonText}>Get Data</Text>
            </TouchableOpacity>
        </View> */}

        <TextInput
          style={styles.input}
          placeholder="Enter event (1500, 400, DT...)"
          placeholderTextColor="#fff"
          value={mainEvent}
          onChangeText={setMainEvent}
        />

        <View style={styles.buttonContainer}>
          <TouchableOpacity style={styles.button} onPress={handleImageUpload}>
          <Text style={styles.buttonText}>Upload {'\n'} Heat Sheet</Text>
          </TouchableOpacity>
        </View>

        <Text style={styles.message}>{message}</Text>

        {/* {imageUri && <Image source={{ uri: imageUri }} style={styles.image} />} */}

      </View>
    );
  }

  const styles = StyleSheet.create({
    container: {
      padding: 30,
      backgroundColor: '#2d2f2f',
      flex: 1,
    },
    title: {
      fontFamily: 'Georgia',
      fontSize: 40,
      color: '#fff',
      textAlign: 'center',
      marginTop: 100,
      marginBottom: 80,
    },
    message: {
      fontFamily: 'Georgia',
      fontSize: 16,
      color: '#fff',
      marginLeft: 10,
      marginTop: 10,
      marginBottom: 5,
      alignSelf: 'center',
    },
    input: {
      alignSelf: 'center',
      height: 40,
      width: '80%',
      borderColor: '#fff',
      borderWidth: 3,
      marginBottom: 20,
      paddingHorizontal: 10,
      fontSize: 18,
      color: '#fff',
      fontFamily: 'Georgia',
    },
    buttonContainer: {
      flexDirection: 'row',
      justifyContent: 'space-evenly',
      marginTop: 20,
      marginBottom: 20,
    },
    button: {
      paddingVertical: 5,
      paddingHorizontal: 20,
      borderColor: '#fff',
      borderWidth: 3,
      borderRadius: 0,
    },
    buttonText: {
      color: '#fff',
      fontSize: 20,
      textAlign: 'center',
      fontFamily: 'Georgia',
    },
    imageButton: { 
      backgroundColor: '#28a745', padding: 12, borderRadius: 8, marginBottom: 16 
    },
    image: { 
      width: 300, height: 300, alignSelf: 'center', marginTop: 20 
    },
  });
  
  export default HomeScreen;