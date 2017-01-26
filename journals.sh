JOURNAL=$1
JOURNAL1=$(echo $JOURNAL | sed 's/ /+/g')
SCIMAGO="http://www.scimagojr.com"
TEMP=$(wget -qO- "$SCIMAGO/journalsearch.php?q=$JOURNAL1")
URL=$(echo $TEMP | awk -F'jrnlname' '{print $2}' | awk -F'a href="' '{print $2}' | awk -F'&clean' '{print $1}')
DATA=$(wget -qO- $SCIMAGO/$URL)
VERIFY1=$(echo $DATA | awk -F'<h1>' '{print $2}' | awk -F'<' '{print $1}')
HINDEX=$(echo $DATA | awk -F'hindexnumber">' '{print $2}' | awk -F'</div>' '{print $1}')
SJR=$(echo $DATA | awk -F'<th>SJR</th>' '{print $2}' | awk -F'<td>2015</td><td>' '{print $2}' | awk -F'</td>' '{print $1}')
CITESPERDOC=$(echo $DATA | awk -F'<td>Cites per document</td><td>2015</td><td>' '{print $2}' | awk -F'</td>' '{print $1}')
EIGENURL="http://eigenfactor.org/projects/journalRank/rankings.php?bsearch=$JOURNAL1&searchby=journal&orderby=eigenfactor"
DATA2=$(wget -qO- $EIGENURL)
VERIFY2=$(echo $DATA2 | awk -F'</div><div class="journal">' '{print $2}' | awk -F'<div' '{print $1}' | tr -s "\n" | tail -n 1)
EIGENF=$(echo $DATA2 | awk -F'pnum1">' '{print $2}' | awk -F'</div>' '{print $1}')
AINFLU=$(echo $DATA2 | awk -F'pnum2">' '{print $2}' | awk -F'</div>' '{print $1}')

if [ 1 -eq "$(echo "${SJR} < 0.06" | bc)" ]
then
	SJRFAST=$(echo "scale=4; ${SJR}/0.06*50" | bc)
elif [ 1 -eq "$(echo "${SJR} >= 0.06" | bc)" ]
then
	if [ 1 -eq "$(echo "${SJR} < 0.07" | bc)" ]
	then
		SJRFAST=50
	elif [ 1 -eq "$(echo "${SJR} >= 0.07" | bc)" ]
	then
		if [ 1 -eq "$(echo "${SJR} < 0.085" | bc)" ]
		then
			SJRFAST=65
		elif [ 1 -eq "$(echo "${SJR} >= 0.085" | bc)" ]
		then
			if [ 1 -eq "$(echo "${SJR} < 0.1" | bc)" ]
			then
				SJRFAST=80
			elif [ 1 -eq "$(echo "${SJR} >= 0.1" | bc)" ]
			then
				SJRFAST=100
			fi
		fi
	fi
fi

if [ 1 -eq "$(echo "${HINDEX} < 40" | bc)" ]
then
	HINDEXFAST=$(echo "scale=4; ${HINDEX}/40*50" | bc)
elif [ 1 -eq "$(echo "${HINDEX} >= 40" | bc)" ]
then
	if [ 1 -eq "$(echo "${HINDEX} < 50" | bc)" ]
	then
		HINDEXFAST=50
	elif [ 1 -eq "$(echo "${HINDEX} >= 50" | bc)" ]
	then
		if [ 1 -eq "$(echo "${HINDEX} < 65" | bc)" ]
		then
			HINDEXFAST=65
		elif [ 1 -eq "$(echo "${HINDEX} >= 65" | bc)" ]
		then
			if [ 1 -eq "$(echo "${HINDEX} < 80" | bc)" ]
			then
				HINDEXFAST=80
			elif [ 1 -eq "$(echo "${HINDEX} >= 80" | bc)" ]
			then
				HINDEXFAST=100
			fi
		fi
	fi
fi

if [ 1 -eq "$(echo "${CITESPERDOC} < 0.5" | bc)" ]
then
	CPDFAST=$(echo "scale=4; ${CITESPERDOC}/1*50" | bc)
elif [ 1 -eq "$(echo "${CITESPERDOC} >= 0.5" | bc)" ]
then
	if [ 1 -eq "$(echo "${CITESPERDOC} < 1" | bc)" ]
	then
		CPDFAST=50
	elif [ 1 -eq "$(echo "${CITESPERDOC} >= 1" | bc)" ]
	then
		if [ 1 -eq "$(echo "${CITESPERDOC} < 1.5" | bc)" ]
		then
			CPDFAST=65
		elif [ 1 -eq "$(echo "${CITESPERDOC} >= 1.5" | bc)" ]
		then
			if [ 1 -eq "$(echo "${CITESPERDOC} < 2" | bc)" ]
			then
				CPDFAST=80
			elif [ 1 -eq "$(echo "${CITESPERDOC} >= 2" | bc)" ]
			then
				CPDFAST=100
			fi
		fi
	fi
fi

TOTAL=$(echo "$AINFLU+$EIGENF+$SJRFAST+$HINDEXFAST+$CPDFAST" | bc)
PERCENTAGE=$(echo "scale=2; $TOTAL/500*100" | bc)

if [ 1 -eq "$(echo "${PERCENTAGE} < 50" | bc)" ]
then
	CATEGORY="Quality Compliant"
elif [ 1 -eq "$(echo "${PERCENTAGE} >= 50" | bc)" ]
then
	if [ 1 -eq "$(echo "${PERCENTAGE} < 60" | bc)" ]
	then
		CATEGORY="Honorable Mention"
	elif [ 1 -eq "$(echo "${PERCENTAGE} >= 60" | bc)" ]
	then
		if [ 1 -eq "$(echo "${PERCENTAGE} < 70" | bc)" ]
		then
			CATEGORY="Bronze"
		elif [ 1 -eq "$(echo "${PERCENTAGE} >= 70" | bc)" ]
		then
			if [ 1 -eq "$(echo "${PERCENTAGE} < 80" | bc)" ]
			then
				CATEGORY="Silver"
			elif [ 1 -eq "$(echo "${PERCENTAGE} >= 80" | bc)" ]
			then
				CATEGORY="Gold"
			fi
		fi
	fi
fi



echo -e "You gave:     $JOURNAL"
echo -e "I found 1:    $VERIFY1"
echo -e "I found 2:    $VERIFY2"
echo -e "If above is not correct, the script has failed."
echo -e ""
echo -e "              Score\tFAST Score"
echo -e "Article Inf:  $AINFLU\t$AINFLU"
echo -e "Eigen Factor: $EIGENF\t$EIGENF"
echo -e "SJR:          $SJR\t$SJRFAST"
echo -e "H-Index:      $HINDEX\t$HINDEXFAST"
echo -e "Cites/Doc:    $CITESPERDOC\t$CPDFAST"
echo -e "                     \t-----"
echo -e "                     \t$TOTAL / 500"
echo -e "                     \t$PERCENTAGE %"
echo -e "                     \t$CATEGORY"
