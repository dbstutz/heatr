import React, { useState } from 'react';
import { StyleSheet, Text, View, Button, StatusBar, useColorScheme, TextInput } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import HomeScreen from './screens/HomeScreen';
import HeatInsights from './screens/HeatInsights';
import AthleteInsights from './screens/AthleteInsights';

const Stack = createStackNavigator();

function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="Home">
        <Stack.Screen name="Home" component={HomeScreen} options={{ headerShown: false }}/>
        <Stack.Screen name="Heat Insights" component={HeatInsights} options={{ headerShown: false }}/>
        <Stack.Screen name="Athlete Insights" component={AthleteInsights} options={{ headerShown: false }}/>
      </Stack.Navigator>
    </NavigationContainer>
  );
}


const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  title: {
    fontSize: 24,
    marginBottom: 20,
  },
  message: {
    marginTop: 20,
    fontSize: 18,
    color: 'blue',
  },
  input: {
    height: 40,
    borderColor: '#aaa',
    borderWidth: 1,
    marginBottom: 10,
    paddingHorizontal: 10,
  },
});

export default App;