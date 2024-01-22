import GlobalNavbar from '../../components/gloabal-navbar/GlobalNavbar';
import HeroCover from './components/hero-cover/HeroCover';
import PopularLocations from './components/popular-locations/popular-locations';
import { networkAdapter } from '../../services/NetworkAdapter';
import { useState, useEffect } from 'react';
import ResultsContainer from '../../components/results-container/ResultsContainer';

const MAX_GUESTS_INPUT_VALUE = 10;

const Home = () => {
  const [isDatePickerVisible, setisDatePickerVisible] = useState(false);
  const [locationInputValue, setLocationInputValue] = useState('Pune');
  const [numGuestsInputValue, setNumGuestsInputValue] = useState('');
  const [popularDestinationsData, setPopularDestinationsData] = useState({
    isLoading: true,
    data: [],
    errors: [],
  });
  const [filtersData, setFiltersData] = useState({
    isLoading: true,
    data: [],
    errors: [],
  });
  const [hotelsResults, setHotelsResults] = useState({
    isLoading: true,
    data: [],
    errors: [],
  });

  const onDatePickerIconClick = () => {
    setisDatePickerVisible(!isDatePickerVisible);
  };

  const onDateSelect = (selection) => {
    console.log(selection);
  };

  const onLocationChangeInput = (newValue) => {
    setLocationInputValue(newValue);
  };

  const onNumGuestsInputChange = (e) => {
    const userInputValue = e.target.value;
    if (userInputValue < MAX_GUESTS_INPUT_VALUE && userInputValue > 0) {
      setNumGuestsInputValue(e.target.value);
    }
  };

  useEffect(() => {
    const getInitialData = async () => {
      const popularDestinationsResponse = await networkAdapter.get(
        '/api/popularDestinations'
      );
      const hotelsResultsResponse =
        await networkAdapter.get('/api/nearbyHotels');

      const filtersDataResponse = await networkAdapter.get(
        'api/hotels/verticalFilters'
      );

      if (popularDestinationsResponse) {
        setPopularDestinationsData({
          isLoading: false,
          data: popularDestinationsResponse.data.elements,
          errors: popularDestinationsResponse.errors,
        });
      }
      if (hotelsResultsResponse) {
        setHotelsResults({
          isLoading: false,
          data: hotelsResultsResponse.data.elements,
          errors: hotelsResultsResponse.errors,
        });
      }
      if (filtersDataResponse) {
        setFiltersData({
          isLoading: false,
          data: filtersDataResponse.data.elements,
          errors: filtersDataResponse.errors,
        });
      }
    };
    getInitialData();
  }, []);

  return (
    <>
      <GlobalNavbar />
      <HeroCover
        locationInputValue={locationInputValue}
        numGuestsInputValue={numGuestsInputValue}
        isDatePickerVisible={isDatePickerVisible}
        onLocationChangeInput={onLocationChangeInput}
        onNumGuestsInputChange={onNumGuestsInputChange}
        onDateSelect={onDateSelect}
        onDatePickerIconClick={onDatePickerIconClick}
      />
      <div className="container mx-auto">
        <PopularLocations popularDestinationsData={popularDestinationsData} />
        <div className="my-8">
          <h2 className="text-3xl font-medium text-slate-700 text-center my-2">
            Handpicked nearby hotels for you
          </h2>
          <ResultsContainer
            hotelsResults={hotelsResults}
            enableFilters={true}
            filtersData={filtersData}
          />
        </div>
      </div>
    </>
  );
};

export default Home;
